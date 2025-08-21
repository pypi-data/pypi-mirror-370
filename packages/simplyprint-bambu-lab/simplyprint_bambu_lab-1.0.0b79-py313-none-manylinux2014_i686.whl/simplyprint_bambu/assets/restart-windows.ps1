param(
    [Parameter(Mandatory=$true)]
    [int]$ProcessId,
    [Parameter(Mandatory=$true)]
    [string]$ProgramExecutable,

    # Save all other parameters to $args
    [Parameter(ValueFromRemainingArguments=$true)][string[]]
    $args
)

function Write-Log {
    param(
        [string]$Message
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "$timestamp $Message"
}

Write-Log "Got process ID: $ProcessId"
Write-Log "Got program executable: $ProgramExecutable"
Write-Log "Got arguments: $args"

Write-Log "Restarting the application, waiting for previous process to exit..."
Wait-Process -Id $ProcessId -Timeout 600

Write-Log "Starting the application..."

if ($args -eq $null -or $args.Length -eq 0) {
    Start-Process -FilePath $ProgramExecutable
} else {
    Start-Process -FilePath $ProgramExecutable -ArgumentList $args
}