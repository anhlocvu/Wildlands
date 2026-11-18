# Full automated verification harness for Wildlands Online (Windows).
# Always cleans up temporary test folders and spawned server processes on exit.

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$Nvgt = "C:\nvgt\nvgt.exe"
$TmpData = Join-Path $Root "tools\_tmp_net_test"
$TestPort = 7199
$ServerProc = $null

function Cleanup-Harness {
    if ($null -ne $script:ServerProc -and -not $script:ServerProc.HasExited) {
        try {
            Stop-Process -Id $script:ServerProc.Id -Force -ErrorAction SilentlyContinue
            Start-Sleep -Milliseconds 150
        } catch {}
    }
    if (Test-Path $TmpData) {
        Remove-Item -Path $TmpData -Recurse -Force -ErrorAction SilentlyContinue
    }
    $TmpProf = Join-Path $Root "tools\_tmp_profile_test"
    if (Test-Path $TmpProf) {
        Remove-Item -Path $TmpProf -Recurse -Force -ErrorAction SilentlyContinue
    }
    $TmpNestedTools = Join-Path $Root "tools\tools"
    if (Test-Path $TmpNestedTools) {
        Remove-Item -Path $TmpNestedTools -Recurse -Force -ErrorAction SilentlyContinue
    }
    $TmpCliSmoke = Join-Path $Root "tools\_tmp_cli_smoke"
    if (Test-Path $TmpCliSmoke) {
        Remove-Item -Path $TmpCliSmoke -Recurse -Force -ErrorAction SilentlyContinue
    }
    $TmpProdData = Join-Path $Root "tools\_tmp_prod_srv"
    if (Test-Path $TmpProdData) {
        Remove-Item -Path $TmpProdData -Recurse -Force -ErrorAction SilentlyContinue
    }
    $TmpProfE2E = Join-Path $Root "tools\_tmp_client_e2e_prof"
    if (Test-Path $TmpProfE2E) {
        Remove-Item -Path $TmpProfE2E -Recurse -Force -ErrorAction SilentlyContinue
    }
}

function Start-TestServer {
    param([int]$Port = $TestPort, [string]$DataDir = $TmpData, [string]$MapsDir = "", [switch]$ProdMode)
    $srvExe = Join-Path $Root "server\server.exe"
    $useMaps = if ($MapsDir.Length -gt 0) { $MapsDir } else { Join-Path $Root "server\maps" }
    $primaryMap = Join-Path $useMaps "wildlands_valley.map"
    $args = @("--headless", "--port", "$Port", "--data-dir", $DataDir, "--maps-dir", $useMaps, "--map", $primaryMap, "--bots", "1", "--wildlife", "8")
    if (-not $ProdMode) { $args = @("--test-mode") + $args }
    $script:ServerProc = Start-Process -FilePath $srvExe -ArgumentList $args -WorkingDirectory $Root -PassThru -WindowStyle Hidden
    $deadline = (Get-Date).AddSeconds(3)
    while ((Get-Date) -lt $deadline) {
        if ($script:ServerProc.HasExited) {
            throw "Test server exited prematurely with code $($script:ServerProc.ExitCode)"
        }
        Start-Sleep -Milliseconds 120
    }
}

function Stop-TestServer {
    if ($null -ne $script:ServerProc -and -not $script:ServerProc.HasExited) {
        Stop-Process -Id $script:ServerProc.Id -Force -ErrorAction SilentlyContinue
        $script:ServerProc.WaitForExit(3000) | Out-Null
    }
    $script:ServerProc = $null
}

try {
    Write-Host "=== 1. Offline Unit Checks ==="
    foreach ($chk in @("tools\common_check.nvgt", "tools\map_check.nvgt", "tools\auth_check.nvgt", "tools\asset_check.nvgt", "tools\client_profile_check.nvgt")) {
        Write-Host "Running $chk..."
        & $Nvgt $chk
        if ($LASTEXITCODE -ne 0) { throw "Check failed: $chk (exit $LASTEXITCODE)" }
    }

    Write-Host "`n=== 2. Compile Server & Client Binaries ==="
    & $Nvgt -c server/server.nvgt
    if ($LASTEXITCODE -ne 0) { throw "Server compile failed" }
    & $Nvgt -c client/client.nvgt
    if ($LASTEXITCODE -ne 0) { throw "Client compile failed" }

    Write-Host "`n=== 3. E2E Network Integration (Phase 1: Handshake, Auth, World, Verticality, Multi-Map, Builder F8, Staff F9) ==="
    if (Test-Path $TmpData) { Remove-Item -Path $TmpData -Recurse -Force }
    New-Item -ItemType Directory -Path $TmpData -Force | Out-Null
    $TmpMaps = Join-Path $TmpData "maps"
    New-Item -ItemType Directory -Path $TmpMaps -Force | Out-Null
    Copy-Item "server\maps\*.map" $TmpMaps -Force
    Copy-Item "server\data\motd.txt" (Join-Path $TmpData "motd.txt") -Force
    Copy-Item "server\data\changelog.txt" (Join-Path $TmpData "changelog.txt") -Force
    Set-Content -Path (Join-Path $TmpData "devs.txt") -Value "TestDev`n"

    Start-TestServer -MapsDir $TmpMaps
    & $Nvgt "tools\net_integration_check.nvgt" -- --phase 1 --port $TestPort
    if ($LASTEXITCODE -ne 0) { throw "Integration Phase 1 failed (exit $LASTEXITCODE)" }
    Stop-TestServer

    Write-Host "`n=== 4. E2E Persistence Across Restart, Graceful Shutdown & Real Client.exe Smoke Tests ==="
    Start-TestServer -MapsDir $TmpMaps
    & $Nvgt "tools\net_integration_check.nvgt" -- --phase 2 --port $TestPort
    if ($LASTEXITCODE -ne 0) { throw "Integration Phase 2 failed (exit $LASTEXITCODE)" }
    if (-not $script:ServerProc.WaitForExit(3500)) {
        throw "Server did not exit cleanly after STAFF|lifecycle|shutdown"
    }
    if ($script:ServerProc.ExitCode -ne 0) {
        throw "Server lifecycle shutdown returned non-zero exit code $($script:ServerProc.ExitCode)"
    }
    $script:ServerProc = $null

    Start-TestServer -MapsDir $TmpMaps
    $TmpCliSmoke = Join-Path $Root "tools\_tmp_cli_smoke"
    $cliExe = Join-Path $Root "client\client.exe"
    Write-Host "Running live compiled client.exe E2E smoke test..."
    $cp = Start-Process -FilePath $cliExe -ArgumentList "--headless","--smoke-test","--host","127.0.0.1","--port","$TestPort","--profile-dir",$TmpCliSmoke -PassThru -Wait
    if ($cp.ExitCode -ne 0) { throw "client.exe headless network smoke test failed (exit $($cp.ExitCode))" }

    Write-Host "Running compiled client.exe windowed & audio init smoke test..."
    $cpw = Start-Process -FilePath $cliExe -ArgumentList "--smoke-test","--profile-dir",$TmpCliSmoke -PassThru -Wait
    if ($cpw.ExitCode -ne 0) { throw "client.exe windowed/audio smoke test failed (exit $($cpw.ExitCode))" }
    Stop-TestServer

    Write-Host "`n=== 5. Client E2E + 18s Form Keepalive Regression Check (Production Mode Server) ==="
    $TmpProd = Join-Path $Root "tools\_tmp_prod_srv"
    if (Test-Path $TmpProd) { Remove-Item -Path $TmpProd -Recurse -Force }
    New-Item -ItemType Directory -Path $TmpProd -Force | Out-Null
    Copy-Item "server\data\motd.txt" (Join-Path $TmpProd "motd.txt") -Force
    Copy-Item "server\data\changelog.txt" (Join-Path $TmpProd "changelog.txt") -Force
    Set-Content -Path (Join-Path $TmpProd "devs.txt") -Value "TestDev`n"

    Start-TestServer -Port 7198 -DataDir $TmpProd -ProdMode
    & $Nvgt "tools\client_ui_e2e_check.nvgt" -- --port 7198
    if ($LASTEXITCODE -ne 0) { throw "Client E2E keepalive/subsystem check failed (exit $LASTEXITCODE)" }
    Stop-TestServer

    Write-Host "`n=== ALL CHECKS PASSED ==="
} finally {
    Cleanup-Harness
}
