"""
MCP Server implementation for Pingera monitoring service.
"""
import logging
import json
from typing import Optional, List

from mcp.server.fastmcp import FastMCP

from config import Config
from pingera_mcp import PingeraClient
from pingera_mcp.tools import PagesTools, StatusTools, ComponentTools, ChecksTools, AlertsTools, HeartbeatsTools, IncidentsTools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("pingera-mcp-server")

# Load configuration
config = Config()

# Validate API key
if not config.api_key:
    logger.error("PINGERA_API_KEY environment variable is required")
    raise ValueError("PINGERA_API_KEY is required")

logger.info(f"Starting Pingera MCP Server in {config.mode} mode")

# Create MCP server
mcp = FastMCP(config.server_name)

# Initialize Pingera client
pingera_client = PingeraClient(
    api_key=config.api_key,
    base_url=config.base_url,
    timeout=config.timeout,
    max_retries=config.max_retries
)
logger.info("Using Pingera SDK client")

# Initialize tool and resource handlers
pages_tools = PagesTools(pingera_client)
status_tools = StatusTools(pingera_client)
component_tools = ComponentTools(pingera_client)
checks_tools = ChecksTools(pingera_client)
alerts_tools = AlertsTools(pingera_client)
heartbeats_tools = HeartbeatsTools(pingera_client)
incidents_tools = IncidentsTools(pingera_client)

# Register read-only tools
@mcp.tool()
async def list_pages(
    page: Optional[int] = None, 
    per_page: Optional[int] = None, 
    status: Optional[str] = None
) -> str:
    """
    List all status pages in your Pingera account.

    This is typically the first tool you should use to discover available pages and their IDs.
    Each page has a unique ID that you'll need for other operations like listing incidents or components.

    Args:
        page: Page number for pagination (default: 1)
        per_page: Number of items per page (default: 20, max: 100)

    Returns:
        JSON with list of status pages including their names, IDs, domains, and configuration details.
    """
    return await pages_tools.list_pages(page, per_page, status)

@mcp.tool()
async def get_page_details(page_id: int) -> str:
    """
    Get detailed information about a specific status page.

    Args:
        page_id: The unique identifier of the status page

    Returns:
        JSON with complete page details including settings, components, branding, and configuration.
    """
    return await pages_tools.get_page_details(page_id)

@mcp.tool()
async def test_pingera_connection() -> str:
    """
    Test the connection to Pingera API and verify authentication.

    Use this tool to verify that your API key is working and the service is accessible.
    It provides connection status, API version info, and any authentication issues.

    Returns:
        JSON with connection status, API information, and authentication details.
    """
    return await status_tools.test_pingera_connection()

@mcp.tool()
async def list_component_groups(
    page_id: str,
    show_deleted: Optional[bool] = False
) -> str:
    """
    Get only component groups (not individual components) for a status page.

    Use this tool specifically when someone asks for "component groups", "groups only", 
    or wants to see just the organizational containers for components. This excludes 
    individual components and shows only the group containers.

    Args:
        page_id: The ID of the status page (required, e.g., "tih6xo7z8v7n")
        show_deleted: Whether to include deleted component groups (default: False)

    Returns:
        JSON with list of component groups only, including their names, IDs, positions, and component counts.
    """
    return await component_tools.list_component_groups(page_id, show_deleted)

@mcp.tool()
async def list_components(
    page_id: str,
    page: Optional[int] = None,
    page_size: Optional[int] = None
) -> str:
    """
    Get all components (individual services and groups) for a status page with their IDs.

    Use this tool when someone asks for "components", "all components", "component list", 
    or wants to see services/systems on a status page. This includes both individual 
    components and component groups with their unique identifiers.

    Args:
        page_id: The ID of the status page (required, e.g., "tih6xo7z8v7n")
        page: Page number for pagination (optional, default: 1)
        page_size: Number of components per page (optional, default: 20)

    Returns:
        JSON with complete list of components including names, IDs, status, type (group/individual), and configuration.
    """
    return await component_tools.list_components(page_id, page, page_size)

@mcp.tool()
async def get_component_details(page_id: str, component_id: str) -> str:
    """
    Get detailed information about a specific component.

    Components represent individual services or systems that are monitored and displayed
    on your status page. Each component has a status and can be linked to monitoring checks.

    Args:
        page_id: The ID of the status page
        component_id: The unique identifier of the component

    Returns:
        JSON with component details including name, description, status, position, and linked checks.
    """
    return await component_tools.get_component_details(page_id, component_id)

@mcp.tool()
async def list_checks(
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    check_type: Optional[str] = None,
    status: Optional[str] = None
) -> str:
    """
    List all monitoring checks in your account.

    Checks are automated tests that monitor your websites, APIs, and services.
    They run at regular intervals and can trigger alerts when issues are detected.

    Args:
        page: Page number for pagination
        page_size: Number of items per page (max: 100)
        check_type: Filter by check type ('http', 'https', 'ping', 'tcp', 'ssl', 'dns', 'keyword')
        status: Filter by status ('active', 'paused', 'disabled')

    Returns:
        JSON with list of checks including names, URLs, types, intervals, and current status.
    """
    return await checks_tools.list_checks(page, page_size, check_type, status)

@mcp.tool()
async def get_check_details(check_id: str) -> str:
    """
    Get detailed configuration and settings for a specific monitoring check.

    Args:
        check_id: The unique identifier of the monitoring check

    Returns:
        JSON with complete check configuration including URL, intervals, timeouts, 
        expected responses, notification settings, and linked components.
    """
    return await checks_tools.get_check_details(check_id)

@mcp.tool()
async def get_check_results(
    check_id: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None
) -> str:
    """
    Get historical results and performance data for a monitoring check.

    This provides detailed execution history including response times, status codes,
    error messages, and uptime statistics for the specified time period.

    Args:
        check_id: The unique identifier of the monitoring check
        from_date: Start date in ISO format (e.g., '2024-01-01T00:00:00Z')
        to_date: End date in ISO format (e.g., '2024-01-31T23:59:59Z')
        page: Page number for pagination
        page_size: Number of results per page

    Returns:
        JSON with check results including timestamps, response times, status codes, and error details.
    """
    return await checks_tools.get_check_results(check_id, from_date, to_date, page, page_size)

@mcp.tool()
async def get_check_statistics(check_id: str) -> str:
    """
    Get statistical summary and performance metrics for a monitoring check.

    Provides uptime percentage, average response time, total executions,
    and other key performance indicators for the check.

    Args:
        check_id: The unique identifier of the monitoring check

    Returns:
        JSON with statistics including uptime %, avg response time, success rate, and error counts.
    """
    return await checks_tools.get_check_statistics(check_id)

@mcp.tool()
async def list_check_jobs() -> str:
    """
    List all currently running or queued check execution jobs.

    Shows the status of scheduled and on-demand check executions,
    useful for monitoring the execution queue and identifying any stuck jobs.

    Returns:
        JSON with list of active jobs including job IDs, check IDs, status, and execution times.
    """
    return await checks_tools.list_check_jobs()

@mcp.tool()
async def get_check_job_details(job_id: str) -> str:
    """
    Get detailed information about a specific check execution job.

    Args:
        job_id: The unique identifier of the check job

    Returns:
        JSON with job details including execution status, start/end times, results, and any errors.
    """
    return await checks_tools.get_check_job_details(job_id)

@mcp.tool()
async def get_unified_results(
    check_ids: Optional[List[str]] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    status: Optional[str] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None
) -> str:
    """
    Get combined results from multiple checks in a unified format.

    Useful for analyzing performance across multiple services or getting
    an overview of all your monitoring data in a single request.

    Args:
        check_ids: List of check IDs to include (if None, includes all checks)
        from_date: Start date in ISO format
        to_date: End date in ISO format  
        status: Filter by result status ('success', 'failure', 'timeout')
        page: Page number for pagination
        page_size: Number of results per page

    Returns:
        JSON with unified results from multiple checks including timestamps and performance data.
    """
    return await checks_tools.get_unified_results(check_ids, from_date, to_date, status, page, page_size)

@mcp.tool()
async def get_unified_statistics(
    check_ids: Optional[List[str]] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
) -> str:
    """
    Get combined statistical summary across multiple monitoring checks.

    Provides aggregated uptime, performance metrics, and trends across
    your entire monitoring infrastructure or a subset of checks.

    Args:
        check_ids: List of check IDs to analyze (if None, includes all checks)
        from_date: Start date for statistics calculation
        to_date: End date for statistics calculation

    Returns:
        JSON with aggregated statistics including overall uptime, avg response times, and trends.
    """
    return await checks_tools.get_unified_statistics(check_ids, from_date, to_date)

@mcp.tool()
async def execute_custom_check(
    url: str,
    check_type: str = "web",
    timeout: Optional[int] = 30,
    name: Optional[str] = None,
    parameters: Optional[dict] = None
) -> str:
    """
    Execute a one-time custom monitoring check on any URL or service.

    This allows you to test connectivity and performance to any endpoint
    without creating a permanent monitoring check. Useful for troubleshooting
    or testing new services before setting up regular monitoring.

    Args:
        url: The URL or endpoint to test
        check_type: Type of check ('web', 'api', 'ping', 'tcp', 'ssl', 'dns')
        timeout: Timeout in seconds (default: 30)
        name: Optional name for the check
        parameters: Additional check-specific parameters

    Returns:
        JSON with immediate check results including response time, status, and any errors.
    """
    return await checks_tools.execute_custom_check(url, check_type, timeout, name, parameters)

@mcp.tool()
async def execute_existing_check(check_id: str) -> str:
    """
    Manually trigger an existing monitoring check to run immediately.

    Forces an immediate execution of a configured check, bypassing the normal
    scheduled interval. Useful for testing after configuration changes or 
    getting fresh data on demand.

    Args:
        check_id: The unique identifier of the check to execute

    Returns:
        JSON with execution job details and immediate results if available.
    """
    return await checks_tools.execute_existing_check(check_id)

@mcp.tool()
async def get_on_demand_job_status(job_id: str) -> str:
    """
    Check the status and results of an on-demand check execution job.

    After triggering a manual check execution, use this to monitor the job
    progress and retrieve results once the execution completes.

    Args:
        job_id: The job ID returned from execute_existing_check or execute_custom_check

    Returns:
        JSON with job status, execution progress, and results if completed.
    """
    return await checks_tools.get_on_demand_job_status(job_id)

@mcp.tool()
async def list_on_demand_checks(
    page: Optional[int] = None,
    page_size: Optional[int] = None
) -> str:
    """
    List all on-demand (manually executed) check jobs and their status.

    Shows recent manual check executions, both custom checks and manually
    triggered existing checks, with their current status and results.

    Args:
        page: Page number for pagination
        page_size: Number of jobs per page

    Returns:
        JSON with list of on-demand check jobs including status, timestamps, and results.
    """
    return await checks_tools.list_on_demand_checks(page, page_size)

@mcp.tool()
async def list_alerts(
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    status: Optional[str] = None
) -> str:
    """
    List all alert configurations in your account.

    Alerts are rules that trigger notifications when monitoring checks fail
    or meet specific conditions. Each alert can be configured with different
    channels, thresholds, and escalation rules.

    Args:
        page: Page number for pagination
        page_size: Number of alerts per page
        status: Filter by alert status ('active', 'paused', 'disabled')

    Returns:
        JSON with list of alerts including names, conditions, notification channels, and status.
    """
    return await alerts_tools.list_alerts(page, page_size, status)

@mcp.tool()
async def get_alert_details(alert_id: str) -> str:
    """
    Get detailed configuration for a specific alert rule.

    Shows complete alert setup including trigger conditions, notification
    channels, escalation rules, and recent activity.

    Args:
        alert_id: The unique identifier of the alert rule

    Returns:
        JSON with alert details including conditions, channels, thresholds, and escalation settings.
    """
    return await alerts_tools.get_alert_details(alert_id)

@mcp.tool()
async def get_alert_statistics() -> str:
    """
    Get statistical overview of all alert activity.

    Provides summary of alert triggers, resolution times, most frequently
    triggered alerts, and overall notification volume.

    Returns:
        JSON with alert statistics including trigger counts, avg resolution time, and trends.
    """
    return await alerts_tools.get_alert_statistics()

@mcp.tool()
async def list_alert_channels() -> str:
    """
    List all configured notification channels for alerts.

    Shows available notification methods like email, SMS, webhooks,
    and their configuration status. These channels are used by alert rules
    to deliver notifications when issues are detected.

    Returns:
        JSON with list of notification channels including types, names, and status.
    """
    return await alerts_tools.list_alert_channels()

@mcp.tool()
async def list_alert_rules() -> str:
    """
    List all alert rules and their trigger conditions.

    Shows the specific conditions and thresholds that will trigger each alert,
    including response time thresholds, uptime requirements, and error conditions.

    Returns:
        JSON with list of alert rules including conditions, thresholds, and linked checks.
    """
    return await alerts_tools.list_alert_rules()

# Register heartbeat tools
@mcp.tool()
async def list_heartbeats(
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    status: Optional[str] = None
) -> str:
    """
    List all heartbeat monitors in your account.

    Heartbeats monitor cron jobs, scheduled tasks, and background processes
    by expecting regular "ping" signals. If a ping is missed, it indicates
    the monitored process may have failed or stopped running.

    Args:
        page: Page number for pagination
        page_size: Number of heartbeats per page
        status: Filter by status ('active', 'inactive', 'grace_period', 'down')

    Returns:
        JSON with list of heartbeats including names, URLs, intervals, and last ping times.
    """
    return await heartbeats_tools.list_heartbeats(page, page_size, status)

@mcp.tool()
async def get_heartbeat_details(heartbeat_id: str) -> str:
    """
    Get detailed information about a specific heartbeat monitor.

    Shows configuration, recent activity, ping history, and current status
    for monitoring cron jobs and scheduled tasks.

    Args:
        heartbeat_id: The unique identifier of the heartbeat monitor

    Returns:
        JSON with heartbeat details including schedule, grace period, last ping, and history.
    """
    return await heartbeats_tools.get_heartbeat_details(heartbeat_id)

@mcp.tool()
async def create_heartbeat(heartbeat_data: dict) -> str:
    """
    Create a new heartbeat monitor for cron jobs or scheduled tasks.

    Set up monitoring for background processes by creating a heartbeat that
    expects regular ping signals. Configure the expected interval and grace period.

    Args:
        heartbeat_data: Dictionary with heartbeat configuration (name, interval, grace_period, etc.)

    Returns:
        JSON with created heartbeat details including the unique ping URL to use in your scripts.
    """
    return await heartbeats_tools.create_heartbeat(heartbeat_data)

@mcp.tool()
async def update_heartbeat(heartbeat_id: str, heartbeat_data: dict) -> str:
    """
    Update configuration for an existing heartbeat monitor.

    Modify settings like expected interval, grace period, notification rules,
    or other heartbeat configuration parameters.

    Args:
        heartbeat_id: The unique identifier of the heartbeat to update
        heartbeat_data: Dictionary with updated heartbeat configuration

    Returns:
        JSON with updated heartbeat details and configuration.
    """
    return await heartbeats_tools.update_heartbeat(heartbeat_id, heartbeat_data)

@mcp.tool()
async def delete_heartbeat(heartbeat_id: str) -> str:
    """
    Delete a heartbeat monitor permanently.

    This will stop monitoring the associated cron job or scheduled task.
    The heartbeat ping URL will become inactive after deletion.

    Args:
        heartbeat_id: The unique identifier of the heartbeat to delete

    Returns:
        JSON confirming successful deletion.
    """
    return await heartbeats_tools.delete_heartbeat(heartbeat_id)

@mcp.tool()
async def send_heartbeat_ping(heartbeat_id: str) -> str:
    """
    Manually send a ping signal to a heartbeat monitor.

    This simulates a successful execution of the monitored process.
    Normally, your cron jobs or scripts would ping the heartbeat URL automatically.

    Args:
        heartbeat_id: The unique identifier of the heartbeat to ping

    Returns:
        JSON confirming the ping was received and recorded.
    """
    return await heartbeats_tools.send_heartbeat_ping(heartbeat_id)

@mcp.tool()
async def get_heartbeat_logs(
    heartbeat_id: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None
) -> str:
    """
    Get historical ping logs and activity for a heartbeat monitor.

    Shows when pings were received, missed pings that triggered alerts,
    and the overall reliability pattern of the monitored process.

    Args:
        heartbeat_id: The unique identifier of the heartbeat
        from_date: Start date in ISO format for log retrieval
        to_date: End date in ISO format for log retrieval
        page: Page number for pagination
        page_size: Number of log entries per page

    Returns:
        JSON with ping history including timestamps, status, and any alert triggers.
    """
    return await heartbeats_tools.get_heartbeat_logs(heartbeat_id, from_date, to_date, page, page_size)

@mcp.tool()
async def list_incidents(
    page_id: str,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    status: Optional[str] = None
) -> str:
    """
    List all incidents for a specific status page.

    Incidents represent service outages, maintenance windows, or other
    events that affect your services and need to be communicated to users
    through your status page.

    Args:
        page_id: The ID of the status page to get incidents for
        page: Page number for pagination
        page_size: Number of incidents per page
        status: Filter by incident status ('investigating', 'identified', 'monitoring', 'resolved')

    Returns:
        JSON with list of incidents including titles, status, impact level, and timestamps.
    """
    return await incidents_tools.list_incidents(page_id, page, page_size, status)

@mcp.tool()
async def get_incident_details(page_id: str, incident_id: str) -> str:
    """
    Get detailed information about a specific incident.

    Shows complete incident details including description, affected components,
    impact level, timeline, and all status updates posted during the incident.

    Args:
        page_id: The ID of the status page
        incident_id: The unique identifier of the incident

    Returns:
        JSON with incident details including description, components, updates, and resolution timeline.
    """
    return await incidents_tools.get_incident_details(page_id, incident_id)

@mcp.tool()
async def get_incident_updates(page_id: str, incident_id: str) -> str:
    """
    Get all status updates posted during an incident.

    Shows chronological list of updates that were posted to keep users
    informed about the incident progress, investigation, and resolution.

    Args:
        page_id: The ID of the status page
        incident_id: The unique identifier of the incident

    Returns:
        JSON with list of incident updates including timestamps, status changes, and messages.
    """
    return await incidents_tools.get_incident_updates(page_id, incident_id)

@mcp.tool()
async def get_incident_update_details(page_id: str, incident_id: str, update_id: str) -> str:
    """
    Get detailed information about a specific incident update.

    Shows the complete content of a specific status update that was posted
    during an incident, including the message, timestamp, and status change.

    Args:
        page_id: The ID of the status page
        incident_id: The unique identifier of the incident
        update_id: The unique identifier of the specific update

    Returns:
        JSON with update details including message content, timestamp, and status information.
    """
    return await incidents_tools.get_incident_update_details(page_id, incident_id, update_id)


# Register write tools only if in read-write mode
if config.is_read_write():
    logger.info("Read-write mode enabled - adding write operations")

    @mcp.tool()
    async def create_page(
        name: str,
        subdomain: Optional[str] = None,
        domain: Optional[str] = None,
        url: Optional[str] = None,
        language: Optional[str] = None
    ) -> str:
        """
        Create a new status page.

        Args:
            name: Display name of the status page (required)
            subdomain: Subdomain for accessing the status page
            domain: Custom domain for the status page
            url: Company URL for logo redirect
            language: Language for the status page interface ("ru" or "en")

        Returns:
            JSON string containing the created page details
        """
        return await pages_tools.create_page(name, subdomain, domain, url, language)

    @mcp.tool()
    async def update_page(
        page_id: str,
        name: Optional[str] = None,
        subdomain: Optional[str] = None,
        domain: Optional[str] = None,
        url: Optional[str] = None,
        language: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Update configuration and settings for an existing status page.

        Modify page properties like name, domain settings, branding, or
        other configuration options. Only specified fields will be updated.

        Args:
            page_id: The unique identifier of the page to update
            name: New name/title for the status page
            subdomain: New subdomain setting
            domain: New custom domain
            url: Updated company/service URL
            language: New language setting
            **kwargs: Additional configuration updates

        Returns:
            JSON with updated page details and configuration.
        """
        return await pages_tools.update_page(page_id, name, subdomain, domain, url, language, **kwargs)

    @mcp.tool()
    async def patch_page(page_id: str, **kwargs) -> str:
        """
        Partially update specific fields of a status page.

        Similar to update_page but for making targeted changes to specific
        configuration fields without specifying all parameters.

        Args:
            page_id: The unique identifier of the page to patch
            **kwargs: Specific fields to update with their new values

        Returns:
            JSON with updated page configuration.
        """
        return await pages_tools.patch_page(page_id, **kwargs)

    @mcp.tool()
    async def delete_page(page_id: str) -> str:
        """
        Permanently delete a status page and all its associated data.

        WARNING: This action cannot be undone. All components, incidents,
        and historical data associated with this page will be deleted.

        Args:
            page_id: The unique identifier of the page to delete

        Returns:
            JSON confirming successful deletion.
        """
        return await pages_tools.delete_page(page_id)

    @mcp.tool()
    async def create_component(
        page_id: str,
        name: str,
        description: Optional[str] = None,
        group: Optional[bool] = False,
        group_id: Optional[str] = None,
        only_show_if_degraded: Optional[bool] = None,
        position: Optional[int] = None,
        showcase: Optional[bool] = None,
        status: Optional[str] = None
    ) -> str:
        """
        Create a new component or component group on a status page.

        Components represent individual services, systems, or features that users
        care about. They can be organized into groups and have their own status.

        Args:
            page_id: The ID of the status page to add the component to
            name: Display name for the component
            description: Optional description of what this component represents
            group: Whether this is a component group (True) or individual component (False)
            group_id: ID of parent group if this component belongs to a group
            only_show_if_degraded: Whether to hide when status is operational
            position: Display order position on the status page
            showcase: Whether to highlight this component prominently
            status: Initial status ('operational', 'degraded_performance', 'partial_outage', 'major_outage')
            **kwargs: Additional component configuration

        Returns:
            JSON with created component details including ID and configuration.
        """
        return await component_tools.create_component(
            page_id=page_id,
            name=name,
            description=description,
            group=group,
            group_id=group_id,
            only_show_if_degraded=only_show_if_degraded,
            position=position,
            showcase=showcase,
            status=status
        )

    @mcp.tool()
    async def update_component(
        page_id: str,
        component_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        group: Optional[bool] = None,
        group_id: Optional[str] = None,
        only_show_if_degraded: Optional[bool] = None,
        position: Optional[int] = None,
        showcase: Optional[bool] = None,
        status: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Update configuration and properties of an existing component.

        Modify component settings like name, description, status, display options,
        or grouping. Only specified fields will be updated.

        Args:
            page_id: The ID of the status page
            component_id: The unique identifier of the component to update
            name: New display name
            description: Updated description
            group: Whether this should be a group or individual component
            group_id: New parent group ID
            only_show_if_degraded: Updated visibility setting
            position: New display position
            showcase: Whether to highlight prominently
            status: New status setting
            **kwargs: Additional configuration updates

        Returns:
            JSON with updated component details and configuration.
        """
        return await component_tools.update_component(
            page_id, component_id, name, description, group, group_id,
            only_show_if_degraded, position, showcase, status, **kwargs
        )

    @mcp.tool()
    async def patch_component(page_id: str, component_id: str, **kwargs) -> str:
        """
        Partially update specific fields of a component.

        Make targeted updates to specific component properties without
        having to specify all configuration parameters.

        Args:
            page_id: The ID of the status page
            component_id: The unique identifier of the component
            **kwargs: Specific fields to update with their new values

        Returns:
            JSON with updated component configuration.
        """
        return await component_tools.patch_component(page_id, component_id, **kwargs)

    @mcp.tool()
    async def delete_component(page_id: str, component_id: str) -> str:
        """
        Delete a component from a status page permanently.

        This removes the component from the status page display and
        deletes all associated historical status data.

        Args:
            page_id: The ID of the status page
            component_id: The unique identifier of the component to delete

        Returns:
            JSON confirming successful deletion.
        """
        return await component_tools.delete_component(page_id, component_id)

    @mcp.tool()
    async def create_check(check_data: dict) -> str:
        """
        Create a new monitoring check to watch a website, API, or service.

        Set up automated monitoring that will test your service at regular
        intervals and alert you when issues are detected.

        Args:
            check_data: Dictionary with check configuration including:
                - name: Check name
                - url: URL to monitor
                - check_type: Type of check ('http', 'https', 'ping', 'tcp', 'ssl', 'dns')
                - interval: Check frequency in seconds
                - timeout: Request timeout in seconds
                - expected_status: Expected HTTP status code
                - keyword: Keyword to look for in response (optional)
                - alert_settings: Notification configuration

        Returns:
            JSON with created check details including ID and configuration.
        """
        return await checks_tools.create_check(check_data)

    @mcp.tool()
    async def update_check(check_id: str, check_data: dict) -> str:
        """
        Update configuration for an existing monitoring check.

        Modify check settings like URL, interval, timeout, alert thresholds,
        or notification preferences.

        Args:
            check_id: The unique identifier of the check to update
            check_data: Dictionary with updated check configuration

        Returns:
            JSON with updated check details and configuration.
        """
        return await checks_tools.update_check(check_id, check_data)

    @mcp.tool()
    async def delete_check(check_id: str) -> str:
        """
        Delete a monitoring check permanently.

        This stops all monitoring for the specified check and removes
        all historical data and results.

        Args:
            check_id: The unique identifier of the check to delete

        Returns:
            JSON confirming successful deletion.
        """
        return await checks_tools.delete_check(check_id)

    @mcp.tool()
    async def pause_check(check_id: str) -> str:
        """
        Temporarily pause a monitoring check without deleting it.

        The check will stop running but all configuration and historical
        data will be preserved. Can be resumed later.

        Args:
            check_id: The unique identifier of the check to pause

        Returns:
            JSON confirming the check has been paused.
        """
        return await checks_tools.pause_check(check_id)

    @mcp.tool()
    async def resume_check(check_id: str) -> str:
        """
        Resume a previously paused monitoring check.

        The check will start running again at its configured interval
        with all previous settings intact.

        Args:
            check_id: The unique identifier of the check to resume

        Returns:
            JSON confirming the check has been resumed.
        """
        return await checks_tools.resume_check(check_id)

    @mcp.tool()
    async def create_alert(alert_data: dict) -> str:
        """
        Create a new alert rule to get notified when issues are detected.

        Set up notifications that will be sent when monitoring checks fail
        or meet specific conditions like response time thresholds.

        Args:
            alert_data: Dictionary with alert configuration including:
                - name: Alert rule name
                - check_ids: List of checks this alert applies to
                - conditions: Trigger conditions (failures, response time, etc.)
                - channels: Notification channels (email, SMS, webhook, etc.)
                - escalation: Escalation rules and delays

        Returns:
            JSON with created alert rule details and configuration.
        """
        return await alerts_tools.create_alert(alert_data)

    @mcp.tool()
    async def update_alert(alert_id: str, alert_data: dict) -> str:
        """
        Update configuration for an existing alert rule.

        Modify alert conditions, notification channels, escalation rules,
        or which checks the alert applies to.

        Args:
            alert_id: The unique identifier of the alert rule to update
            alert_data: Dictionary with updated alert configuration

        Returns:
            JSON with updated alert rule details and configuration.
        """
        return await alerts_tools.update_alert(alert_id, alert_data)

    @mcp.tool()
    async def delete_alert(alert_id: str) -> str:
        """
        Delete an alert rule permanently.

        This stops all notifications from this alert rule and removes
        the configuration. Historical alert activity may be preserved.

        Args:
            alert_id: The unique identifier of the alert rule to delete

        Returns:
            JSON confirming successful deletion.
        """
        return await alerts_tools.delete_alert(alert_id)

    @mcp.tool()
    async def create_incident(page_id: str, incident_data: dict) -> str:
        """
        Create a new incident on a status page to communicate issues to users.

        Post an incident when you need to inform users about service outages,
        maintenance, or other events affecting your services.

        Args:
            page_id: The ID of the status page to post the incident on
            incident_data: Dictionary with incident details including:
                - name: Incident title
                - status: Current status ('investigating', 'identified', 'monitoring', 'resolved')
                - impact: Impact level ('none', 'minor', 'major', 'critical')
                - body: Initial incident description
                - component_ids: List of affected component IDs
                - deliver_notifications: Whether to send notifications

        Returns:
            JSON with created incident details including ID and public URL.
        """
        return await incidents_tools.create_incident(page_id, incident_data)

    @mcp.tool()
    async def update_incident(page_id: str, incident_id: str, incident_data: dict) -> str:
        """
        Update an existing incident's details and status.

        Modify the incident title, status, impact level, or other properties.
        For status updates that users will see, use add_incident_update instead.

        Args:
            page_id: The ID of the status page
            incident_id: The unique identifier of the incident
            incident_data: Dictionary with updated incident configuration

        Returns:
            JSON with updated incident details.
        """
        return await incidents_tools.update_incident(page_id, incident_id, incident_data)

    @mcp.tool()
    async def delete_incident(page_id: str, incident_id: str) -> str:
        """
        Delete an incident from a status page permanently.

        This removes the incident and all its updates from the status page.
        Use with caution as this action cannot be undone.

        Args:
            page_id: The ID of the status page
            incident_id: The unique identifier of the incident to delete

        Returns:
            JSON confirming successful deletion.
        """
        return await incidents_tools.delete_incident(page_id, incident_id)

    @mcp.tool()
    async def add_incident_update(page_id: str, incident_id: str, update_data: dict) -> str:
        """
        Add a new status update to an existing incident.

        Post updates to keep users informed about incident progress,
        investigation findings, or resolution steps.

        Args:
            page_id: The ID of the status page
            incident_id: The unique identifier of the incident
            update_data: Dictionary with update details including:
                - body: The update message text
                - status: New incident status if changed
                - deliver_notifications: Whether to notify subscribers

        Returns:
            JSON with created update details including timestamp and content.
        """
        return await incidents_tools.add_incident_update(page_id, incident_id, update_data)

    @mcp.tool()
    async def update_incident_update(page_id: str, incident_id: str, update_id: str, update_data: dict) -> str:
        """
        Edit an existing incident status update.

        Modify the content or status of a previously posted incident update.
        Useful for correcting typos or adding additional information.

        Args:
            page_id: The ID of the status page
            incident_id: The unique identifier of the incident
            update_id: The unique identifier of the update to modify
            update_data: Dictionary with updated content and settings

        Returns:
            JSON with updated incident update details.
        """
        return await incidents_tools.update_incident_update(page_id, incident_id, update_id, update_data)

    @mcp.tool()
    async def delete_incident_update(page_id: str, incident_id: str, update_id: str) -> str:
        """
        Delete a specific incident status update.

        Remove an incident update from the timeline. This action cannot
        be undone and may confuse users if the update was already public.

        Args:
            page_id: The ID of the status page
            incident_id: The unique identifier of the incident
            update_id: The unique identifier of the update to delete

        Returns:
            JSON confirming successful deletion.
        """
        return await incidents_tools.delete_incident_update(page_id, incident_id, update_id)