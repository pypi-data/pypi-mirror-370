from dtlpymcp import DataloopContext, MCPSource
import requests
import dtlpy as dl
import asyncio


def test_url_and_headers():
    dl_context = DataloopContext(token=dl.token())
    dl_context.add_mcp_source(MCPSource(dpk_name="dataloop-mcp", app_url=None, app_jwt=None, server_url=None))
    print(dl_context.mcp_sources[0].app_jwt)
    print(dl_context.mcp_sources[0].server_url)
    print(dl_context.mcp_sources[0].app_url)
    headers = {"Cookie": f"JWT-APP={dl_context.mcp_sources[0].app_jwt}", "x-dl-info": dl_context.token}
    health_check_url = dl_context.mcp_sources[0].server_url.replace("/mcp/", "/health")
    response = requests.get(health_check_url, headers=headers)
    print(response.json())


def test_discover_tools_for_server():
    dl_context = DataloopContext(token=dl.token())
    dl_context.add_mcp_source(MCPSource(dpk_name="dataloop-mcp", app_url=None, app_jwt=None, server_url=None))

    result = asyncio.run(dl_context.discover_tools_for_server(dl_context.mcp_sources[0]))
    print(result)


if __name__ == "__main__":
    import dtlpy as dl

    dl.setenv('rc')
    if dl.token_expired():
        dl.login()
    # test_url_and_headers()
    test_discover_tools_for_server()
