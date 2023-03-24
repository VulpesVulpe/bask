import sentry_sdk

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 YaBrowser/23.1.3.949 Yowser/2.5 Safari/537.36"
}

sentry_sdk.init(
    dsn="https://6e46da13998f4929979f90d8718a49ef@o4504872656044032.ingest.sentry.io/4504872658665472",
    traces_sample_rate=1.0
)
