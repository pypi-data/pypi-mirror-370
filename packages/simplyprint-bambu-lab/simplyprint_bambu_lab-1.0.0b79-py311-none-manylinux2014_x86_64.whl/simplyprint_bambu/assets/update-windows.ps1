param(
    [Parameter(Mandatory=$true)]
    [int]$ProcessId,
    [Parameter(Mandatory=$true)]
    [string]$TemporarySourcePath,
    [string]$DestinationPath = "C:\Program Files\SimplyPrint Bambu Lab",
    [string]$ProgramExecutableName = "simplyprint-bambu-lab.exe",
    $DoDryRun = $false
)

function Write-Log {
    param(
        [string]$Message
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "$timestamp $Message"
}

function Invoke-DryRun {
    param(
        [Parameter(Mandatory=$true)]
        [scriptblock]$ScriptBlock
    )

    Write-Log "EXEC: $($ScriptBlock -replace '\s+', ' ')"

    if (!$DoDryRun) {
        # Execute the command
        return Invoke-Command $ScriptBlock
    }
}


function Copy-UpdatedFiles {
    Write-Log "Copying updated files..."
    # Ensure the destination folder exists
    if (-Not (Test-Path -Path $DestinationPath)) {
        Invoke-DryRun { New-Item -ItemType Directory -Force -Path $DestinationPath }
    }

    # Remove the destination folder if it already exists (exclude update.log file)
    if (Test-Path -Path $DestinationPath) {
        Invoke-DryRun {
            Get-ChildItem -Path $DestinationPath | Where-Object { $_.Name -ne "update.log" } | Remove-Item -Recurse -Force
        }
    }

    # Copy the updated folder to the destination
    Invoke-DryRun {
        Copy-Item -Path $TemporarySourcePath\* -Destination $DestinationPath -Recurse -Force
    }
}

function Cleanup-TemporaryFiles {
    Write-Log "Cleaning up temporary files..."
    # Remove the temporary folder
    Invoke-DryRun { Remove-Item -Path $TemporarySourcePath -Recurse -Force }
}

function Start-Application {
    Write-Log "Starting the application..."
    Invoke-DryRun { Start-Process -FilePath $ExecutablePath }
}

Start-Transcript -Path "C:\Program Files\SimplyPrint Bambu Lab\update.log" -Append

Write-Log "Current working directory: $(Get-Location)"

$NewExecutablePath = Join-Path $TemporarySourcePath $ProgramExecutableName
$ExecutablePath = Join-Path $DestinationPath $ProgramExecutableName

# Check if new executable exists
if (-Not (Test-Path -Path $NewExecutablePath)) {
    Write-Log "New executable not found at: $NewExecutablePath"
    exit 1
}

# Get its version by invoking it with "version" as the only arg
$NewVersion = & $NewExecutablePath version | Out-String
$NewVersion = $NewVersion.Trim()

Write-Log "Updating SimplyPrint Bambu Lab client to new version: $NewVersion"

Write-Log "Previous ProcessId: $ProcessId"
Write-Log "DestinationPath: $DestinationPath"
Write-Log "TemporarySourcePath: $TemporarySourcePath"
Write-Log "ExecutablePath: $ExecutablePath"

Write-Log "Waiting for the process to exit... Timeout is 10 minutes"

Wait-Process -Id $ProcessId -ErrorAction SilentlyContinue -Timeout 600

Write-Log "Process exited. Performing update"

# Execute the functions
Copy-UpdatedFiles
Start-Application
Cleanup-TemporaryFiles

Stop-Transcript