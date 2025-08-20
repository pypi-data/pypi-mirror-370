from uncountable.integration.db.connect import IntegrationDBService, create_db_engine
from uncountable.integration.scan_profiles import load_profiles
from uncountable.integration.server import IntegrationServer


def main() -> None:
    with IntegrationServer(create_db_engine(IntegrationDBService.CRON)) as server:
        server.register_jobs(load_profiles())
        server.serve_forever()


if __name__ == "__main__":
    main()
