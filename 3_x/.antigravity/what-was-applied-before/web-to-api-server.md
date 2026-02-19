irflow 3.x Docker Compose Fix Plan
Problem
The astro dev start command failed with:

service "webserver" has neither an image nor a build context specified

This is because in Airflow 3 (Astro Runtime), the webserver service has been renamed to api-server (reflecting the new API-first architecture). The 
docker-compose.override.yml
 tries to override webserver, which no longer exists in the base configuration, thus causing Docker to treat it as a new, incomplete service.

Documentation Reference
Source: Astro Runtime Release Notes / Airflow 3 Migration Guide (General reference)
Specific Change: "For Airflow 3 based Astro Runtime versions, the service name is api-server."
Proposed Changes
migration-3_x/docker-compose.override.yml
Rename Service: Change webserver to api-server.
Remove Obsolete Field: Remove version: "3.1" to fix the warning.
yaml
# Before
version: "3.1"
services:
  webserver:
    networks:
      - ndsnet
# After
services:
  api-server: # Renamed from webserver for Airflow 3
    networks:
      - ndsnet
Verification Plan
Manual Verification
Run: cd migration-3_x && astro dev start
Expectation: The error regarding "webserver" should disappear. The containers should start, and api-server should be attached to ndsnet.

Comment
Ctrl+Alt+M
