from fastmcp import FastMCP
from obshell import ClientSet
from obshell.auth import PasswordAuth
from obshell.model.tenant import ZoneParam
from typing import Dict, Any
import os
import time
import sys


mcp = FastMCP("obshell-mcp")

client = None
SYS_PASSWORD = os.getenv("SYS_PASSWORD", "password")
OBSHELL_HOST = os.getenv("OBSHELL_HOST", "127.0.0.1")
OBSHELL_PORT = os.getenv("OBSHELL_PORT", "2886")
OBSHELL_PORT = int(OBSHELL_PORT)
CLUSTER_NAME = os.getenv("CLUSTER_NAME", "cluster")
TENANT_NAME = os.getenv("TENANT_NAME", "tenant")


create_cluster_desc = f"""Creates a new obcluster.The cluster name has been offered by user: {CLUSTER_NAME}
    创建一个 ob 集群。该方法的响应时间有点长，最长不超过5分钟，当该方法中断或者超时的时候，后续应该先检查集群是否创建成功。
    如果节点身份是 CLUSTER AGENT，则表示集群已经创建成功。
    使用该方法时，应该让用户能够对参数进行修改。
    当用户没有指定对应参数时：
    1. 只启用本地127.0.0.1:2886上的节点, 不用启动其他多余的节点
    2. servers_with_configs 默认使用 {{'127.0.0.1:2886': {{"zone": "zone1",  "datafile_size": "8G", "cpu_count": "8",
            "memory_limit": "7G", "system_memory": "1G", "log_disk_size": "24G",
            "enable_syslog_recycle": "true", "enable_syslog_wf": "true", "__min_full_resource_pool_memory: "1073741824"}}}}
        注意参数都使用字符串类型。
            
    Creates a new obcluster with the specified servers and configurations.

    Args:
        servers_with_configs (list): The dict of the server and its configurations.
            The configuration should include the zone of the server.
            Example: {{'127.0.0.1:2886': {{"zone": "zone1",  "datafile_size": "32G", "cpu_count": "8",
            "memory_limit": "7G", "system_memory": "1G", "log_disk_size": "32G",
            "enable_syslog_recycle": "true", "enable_syslog_wf": "true", "__min_full_resource_pool_memory: 1073741824}}}}
        cluster_id (int): The id of the obcluster.

    Returns:
        Task detail as task.DagDetailDTO.

    Raises:
        OBShellHandleError: error message return by OBShell server.
        TaskExecuteFailedError: raise when the task failed,
            include the failed task detail and logs.
        IllegalOperatorError: raise when the operator is illegal.
"""

create_tenant_desc = f"""Create a tenant synchronously.The tenant name has been offered by user: {TENANT_NAME}
    Creates a tenant with the specified name and zone list.
    创建业务租户时，需要指定所使用的 unit config。
    当用户没有指定对应参数时：
    1. 推荐使用参数：{{ memory_size: 2G; cpu_count: 1; unit_num: 1; "zone_replica_type": {{"zone1":"FULL"}}}}， 其他参数可以随意填写
    2. variables参数和parameters参数留空

    Args:
        zone_replica_type (Dict[str, str]): The map of the zone and its replica type(FULL or READONLY), default is FULL.
        memory_size (str, optional): The memory size when create a new unit config.
        cpu_count (int, optional): The cpu count when create a new unit config.
        unit_num (int, optional): The unit number when create a new unit config.
        log_disk_size (str, optional): The log disk size when create a new unit config.
        mode (str, optional): 
            The mode of the tenant, "MYSQL" or "ORACLE". Defaults to 'MYSQL'.
        primary_zone (str, optional): 
            The primary zone of the tenant. Defaults to "RANDOM".
        whitelist (str, optional): 
            The whitelist of the tenant. Defaults to "%".
        scenario:
            The scenario of the tenant.
            Can be one of 'express_oltp', 'complex_oltp', 'olap', 'htap', 'kv'.
            Defaults to 'oltp'.
        root_password (str, optional): 
            The root password of the tenant. Defaults to Empty.
        import_script (bool, optional):
            Whether need to import the observer's script. Defaults to False.
            Support from OBShell V4.2.4.2.
        charset (str, optional): The charset of the tenant.
            If not set, the charset will be set to default value by observer.
        collation (str, optional): The collation of the tenant.
            If not set, the collation will be set to default value by observer.
        read_only (bool, optional): 
            Whether the tenant is read only. Defaults to False.
        comment (str, optional): The comment of the tenant.

    Returns:
        Task detail as task.DagDetailDTO.

    Raises:
        OBShellHandleError: error message return by OBShell server.
        TaskExecuteFailedError: raise when the task failed,
            include the failed task detail and logs.
"""


# @mcp.tool()
def connect(
    host: str = OBSHELL_HOST,
    port: int = OBSHELL_PORT,
    password: str = SYS_PASSWORD,
    timeout: int = 600,
):
    """连接 obshell 服务
    参数:
        host: obshell 服务地址, 默认为 "127.0.0.1"
        port: obshell 服务端口, 默认为 "2886"
        password: sys 租户的 root 密码, 默认为
        timeout: 时间戳超时时间，单位为秒，默认 600 秒
    返回:
        client: obshell 客户端实例，后续所有 obshell 的 sdk 方法，都需要使用该实例
        当 client 连接成功后，会自动创建一个 obshell 的 session，后续所有 obshell 的 sdk 方法，都需要使用该 session。
        当该 session 使用出错时，需要重新调用 connect 方法，重新创建一个 session。
    """
    global client
    client = ClientSet(host, port, auth=PasswordAuth(password), timeout=timeout)
    try:
        client.v1.get_ob_info()
    except Exception as e:
        raise Exception("连接 obshell 服务失败: " + str(e))
    return client.v1.get_status()


@mcp.tool(description=create_cluster_desc)
def create_cluster(servers_with_configs: dict, cluster_id: int):
    root_pwd = SYS_PASSWORD
    global client
    if client is None:
        connect()
    try:
        client.v1.agg_create_cluster(
            servers_with_configs,
            CLUSTER_NAME,
            cluster_id,
            root_pwd,
            clear_if_failed=True,
        )
    except Exception as e:
        raise Exception("创建 ob 集群失败: " + str(e))
    client.v1._reset_auth()
    return "success!"


@mcp.tool(description=create_tenant_desc)
def create_tenant(
    zone_replica_type: Dict[str, str],
    memory_size: str = "2G",
    cpu_count: int = 1,
    unit_num: int = 1,
    log_disk_size: str = "",
    mode: str = "MYSQL",
    primary_zone: str = "RANDOM",
    whitelist: str = "%",
    scenario: str = None,
    import_script: bool = False,
    charset: str = None,
    collation: str = None,
    read_only: bool = False,
    comment: str = None,
    variables: dict = None,
    parameters: dict = None,
):
    # Global variable `secure_file_priv` take a while to take effect, so we set it early (right after tenant creation)
    # if not variables:
    #     variables = {}
    # variables["secure_file_priv"] = "/"

    root_password = SYS_PASSWORD
    global client
    if client is None:
        connect()

    # 创建一个新的 unit config
    unit_config_name = f"{TENANT_NAME}_unit_config_{int(time.time())}"
    client.v1.create_resource_unit_config(
        unit_config_name,
        memory_size,
        cpu_count,
        log_disk_size=(None if log_disk_size == "" else log_disk_size),
    )

    zone_list = [
        ZoneParam(zone, unit_config_name, unit_num, zone_replica_type.get(zone, "FULL"))
        for zone in zone_replica_type
    ]
    return client.v1.create_tenant_sync(
        TENANT_NAME,
        zone_list,
        mode,
        primary_zone,
        whitelist,
        root_password,
        scenario,
        import_script,
        charset,
        collation,
        read_only,
        comment,
        variables,
        parameters,
    )


@mcp.tool()
def get_all_obshell_sdk_methods():
    """获取 obshell 所有可供用户使用的 sdk 方法
    只有当其他的 tool 不适用时，才通过该方法获取所有 sdk 方法。
    """
    global client
    if client is None:
        connect()
    methods = {}
    for method in dir(client.v1):
        if not method.startswith("_") and not method.startswith("agg"):
            methed = getattr(client.v1, method)
            if callable(methed):
                methods[method] = methed.__doc__
    return methods


@mcp.tool()
def get_obshell_sdk_methods_description(sdk_method: str):
    """获取 obshell 的 sdk 方法的描述"""
    global client
    if client is None:
        connect()
    methed = getattr(client.v1, sdk_method)
    if not callable(methed):
        raise Exception("sdk 方法不存在: " + sdk_method)
    return methed.__doc__


@mcp.tool()
def call_obshell_sdk(sdk_method: str, args: Dict[str, Any]):
    """调用 obshell 的 sdk 方法
    参数:
        sdk_method: obshell 的 sdk 方法名，请根据 sdk 的描述文档，选择一个合适的 sdk 方法。
        args: obshell 的 sdk 方法参数，参数名和参数值需要使用 map 格式，例如: {"arg1": "value1", "arg2": "value2"}
            如果有任何必选参数没有设置，都直接返回错误信息，不要尝试调用 obshell 的 sdk 方法。
    返回:
        result: obshell 的 sdk 方法返回结果
    """
    if client is None:
        connect()
    print("调用 obshell 的 sdk 方法: " + sdk_method)

    # 转换特殊参数格式
    processed_args = args.copy()

    # 如果有 zone_list 参数，转换为 ZoneParam 对象列表
    if "zone_list" in processed_args and isinstance(processed_args["zone_list"], list):
        zone_objects = []
        for zone_data in processed_args["zone_list"]:
            if isinstance(zone_data, dict):
                # 创建 ZoneParam 对象
                zone_name = zone_data.get("zone")
                unit_config_name = zone_data.get(
                    "unit_config", zone_data.get("unit_config_name")
                )
                unit_num = zone_data.get("unit_num", 1)
                replica_type = zone_data.get("replica_type")

                if zone_name and unit_config_name:
                    zone_param = ZoneParam(
                        zone_name, unit_config_name, unit_num, replica_type
                    )
                    zone_objects.append(zone_param)
                else:
                    raise Exception(
                        "zone_list 参数格式错误：缺少必要字段 zone 或 unit_config/unit_config_name"
                    )
            else:
                zone_objects.append(zone_data)  # 已经是对象
        processed_args["zone_list"] = zone_objects

    try:
        return getattr(client.v1, sdk_method)(**processed_args)
    except Exception as e:
        raise Exception("调用 obshell 的 sdk 方法失败: " + str(e))


def main():
    SSE = False
    SSE_PORT = 8000
    if len(sys.argv) > 1 and sys.argv[1] == "--sse":
        SSE = True
        if len(sys.argv) > 2:
            SSE_PORT = int(sys.argv[2])
        else:
            SSE_PORT = 8000
    if SSE:
        mcp.run(transport="sse", host="0.0.0.0", port=SSE_PORT, path="/obshell")
    else:
        mcp.run()


if __name__ == "__main__":
    main()
