# 本机安装目录；数据库数据保存在仓库之外。
$ErrorActionPreference = 'Stop'
$pgRoot = Join-Path $env:LOCALAPPDATA 'fastapi-learning-postgres'
$pgCtl = Join-Path $pgRoot 'pgsql\bin\pg_ctl.exe'
$pgData = Join-Path $pgRoot 'data'
if (-not (Test-Path $pgCtl) -or -not (Test-Path (Join-Path $pgData 'PG_VERSION'))) {
    throw 'Local PostgreSQL is not initialized. See README.'
}
& $pgCtl -D $pgData status
if ($LASTEXITCODE -ne 0) {
    & $pgCtl -D $pgData -l (Join-Path $pgRoot 'postgres.log') -w start
    if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL failed to start.' }
}
