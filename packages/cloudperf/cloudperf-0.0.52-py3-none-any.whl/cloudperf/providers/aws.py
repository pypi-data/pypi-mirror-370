from __future__ import absolute_import
import botocore.session
import cachetools
import requests
from datetime import datetime
from cloudperf.providers import aws_helpers

# link to the newest endpoints.json in case the installed botocore doesn't
# yet have a region
ENDPOINTS_URL = "https://raw.githubusercontent.com/boto/botocore/develop/botocore/data/endpoints.json"


# botocore's endpoints contain some locations with a different name, so provide a base here
region_map = {
    "AWS GovCloud (US)": "us-gov-west-1",
    "AWS GovCloud (US-East)": "us-gov-east-1",
    "AWS GovCloud (US-West)": "us-gov-west-1",
    "Africa (Cape Town)": "af-south-1",
    "Asia Pacific (Hong Kong)": "ap-east-1",
    "Asia Pacific (Hyderabad)": "ap-south-2",
    "Asia Pacific (Mumbai)": "ap-south-1",
    "Asia Pacific (Osaka)": "ap-northeast-3",
    "Asia Pacific (Seoul)": "ap-northeast-2",
    "Asia Pacific (Singapore)": "ap-southeast-1",
    "Asia Pacific (Sydney)": "ap-southeast-2",
    "Asia Pacific (Tokyo)": "ap-northeast-1",
    "Canada (Central)": "ca-central-1",
    "Canada West (Calgary)": "ca-west-1",
    "EU (Frankfurt)": "eu-central-1",
    "EU (Ireland)": "eu-west-1",
    "EU (London)": "eu-west-2",
    "EU (Milan)": "eu-south-1",
    "EU (Paris)": "eu-west-3",
    "EU (Stockholm)": "eu-north-1",
    "Europe (Spain)": "eu-south-2",
    "Europe (Zurich)": "eu-central-2",
    "Israel (Tel Aviv)": "il-central-1",
    "Middle East (Bahrain)": "me-south-1",
    "Middle East (UAE)": "me-central-1",
    "South America (Sao Paulo)": "sa-east-1",
    "US East (N. Virginia)": "us-east-1",
    "US East (Ohio)": "us-east-2",
    "US West (Los Angeles)": "us-west-2-lax-1",
    "US West (N. California)": "us-west-1",
    "US West (Oregon)": "us-west-2",
}

location_map = {v: k for k, v in region_map.items()}


@cachetools.cached(cache={})
def get_endpoints_json():
    return requests.get(ENDPOINTS_URL).json()


@cachetools.cached(cache={})
def resolve_endpoint(region=None, location=None):
    if region in location_map:
        return location_map[region]
    if location in region_map:
        return region_map[location]

    session = botocore.session.get_session()
    endpoint_data = session.get_data("endpoints")

    for _ in range(2):
        for p in endpoint_data.get("partitions", []):
            for r, data in p["regions"].items():
                # the pricing API returns EU, while endpoints contain Europe
                loc = data["description"].replace("Europe", "EU")
                if region == r:
                    return loc
                if location == loc:
                    return r
        # fall back to the latest JSON
        endpoint_data = get_endpoints_json()


def region_to_location(region):
    return resolve_endpoint(region=region)


def location_to_region(location):
    return resolve_endpoint(location=location)


class CloudProvider(object):
    provider = 'aws'
    filters = {'operatingSystem': 'Linux', 'preInstalledSw': 'NA',
               'licenseModel': 'No License required', 'capacitystatus': 'Used',
               'tenancy': 'Shared'
               }

    def get_prices(self, fail_on_missing_regions=False, **filters):
        if not filters:
            filters = self.filters
        instances = aws_helpers.get_ec2_prices(fail_on_missing_regions=fail_on_missing_regions, **filters)
        # add a provider column
        instances['provider'] = self.provider

        return instances

    def get_performance(self, prices_df, perf_df=None, update=None, expire=None, tags=[], **filters):
        if not filters:
            filters = self.filters
        # only pass our records
        prices_df = prices_df[prices_df['provider'] == self.provider]
        if perf_df is not None:
            perf_df = perf_df[perf_df['provider'] == self.provider]
        instances = aws_helpers.get_ec2_performance(prices_df, perf_df, update, expire, tags, **filters)
        if instances.empty:
            return instances
        # add a provider column
        instances['provider'] = self.provider
        return instances

    def terminate_instances(self):
        aws_helpers.terminate_instances()
