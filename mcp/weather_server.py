from mcp.server.fastmcp import FastMCP

mcp=FastMCP("weather_server")

@mcp.tool()
def weather(location:str):
    """this tool will give you weather detail of the provided location"""
    return f"today the wether is at the {location} is sunny!"

if __name__=="__main__":
    mcp.run(transport="streamable-http")