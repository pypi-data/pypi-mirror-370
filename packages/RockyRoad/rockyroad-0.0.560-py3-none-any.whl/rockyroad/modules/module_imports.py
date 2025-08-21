import os


def get_key(use_services_api=False):

    try:
        standard_key = os.environ["OCP_APIM_SUBSCRIPTION_KEY"]
        services_key = os.environ["OCP_APIM_SERVICES_SUBSCRIPTION_KEY"]
    except KeyError as e:
        print(
            f"""ERROR: Define the environment variable {e} with your subscription key.  For example:

        export OCP_APIM_SUBSCRIPTION_KEY="INSERT_YOUR_SUBSCRIPTION_KEY"

        """
        )
        standard_key = None
        services_key = None
    if use_services_api:
        key = services_key
    else:
        key = standard_key
    return key


key = get_key()
