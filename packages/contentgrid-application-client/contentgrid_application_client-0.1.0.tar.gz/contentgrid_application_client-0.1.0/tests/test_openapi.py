from contentgrid_application_client import ContentGridApplicationClient
from fixtures import auth_manager, cg_client # noqa: F401
import os


def test_fetch_openapi_spec(cg_client: ContentGridApplicationClient):
    filename, file = cg_client.fetch_openapi_yaml()
    os.makedirs("output", exist_ok=True)
    output_path = os.path.join("output", filename)
    with open(output_path, 'wb') as f:
        f.write(file)
    assert os.path.exists(output_path)
