from mcp.server.fastmcp import FastMCP

mcp=FastMCP("math_server")

@mcp.tool()
def add(a:int,b:int):
    """this toool is responsible for addition of two numbers"""
    return a+b

@mcp.tool() # it egsiter the python fucntion as mcp tool
def multiply(a:int,b:int):
    """this tool is responsible for multiplication of two numbers"""
    return a*b

if __name__=="__main__":
    mcp.run(transport='stdio') # here the transport is stdio means std input and output so the results will be in cmd

# here the above functions are the tools that this math server will provide
# mcp server will run in the terminal but to exucuteits tool we need to connect mcp client