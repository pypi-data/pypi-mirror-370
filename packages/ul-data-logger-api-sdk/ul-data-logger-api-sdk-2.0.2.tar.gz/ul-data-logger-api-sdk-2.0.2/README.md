# ul_iot_account_data_logger

## Restoring the db dump

1) add your dump to ./tmp
2) run bash in manager
    ```bash
   docker-compose run --rm manager__data_logger__db bash
   ```
3) run inside of manager
    ```bash
    pg_restore -U admin -h data_logger__db -d data_logger_db -p 5432 -1 --data-only -t device_log /temporary/dump.sql
    ```
