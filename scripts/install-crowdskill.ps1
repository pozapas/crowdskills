[CmdletBinding()]
param(
    [ValidateSet("jupedsim", "pedpy", "petrack", "viswalk-com", "pathfinder", "massmotion", "evacuationz")]
    [string[]] $Skill,

    [switch] $All,

    [string] $DestinationRoot,

    [string] $ProjectRoot,

    [switch] $List
)

$ErrorActionPreference = "Stop"

if ($DestinationRoot -and $ProjectRoot) {
    throw "Use either -DestinationRoot or -ProjectRoot, not both."
}

$repoRoot = Split-Path -Parent $PSScriptRoot

$skillSources = [ordered]@{
    "jupedsim"    = "jupedsim\jupedsim"
    "pedpy"       = "pedpy\pedpy"
    "petrack"     = "petrack\petrack"
    "viswalk-com" = "viswalk-com\viswalk-com"
    "pathfinder"  = "pathfinder\pathfinder"
    "massmotion"  = "massmotion\massmotion"
    "evacuationz" = "evacuationz"
}

if ($ProjectRoot) {
    $DestinationRoot = Join-Path $ProjectRoot ".agents\skills"
}
elseif (-not $DestinationRoot) {
    $DestinationRoot = Join-Path $HOME ".agents\skills"
}

New-Item -ItemType Directory -Force -Path $DestinationRoot | Out-Null
$destinationRootFull = [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $DestinationRoot).Path)

if ($List) {
    $skillSources.GetEnumerator() | ForEach-Object {
        $source = Join-Path $repoRoot $_.Value
        [PSCustomObject]@{
            Skill       = $_.Key
            Source      = $source
            Destination = Join-Path $destinationRootFull $_.Key
            HasSkillMd  = Test-Path -LiteralPath (Join-Path $source "SKILL.md")
        }
    }
    return
}

if ($All) {
    $Skill = @($skillSources.Keys)
}

if (-not $Skill -or $Skill.Count -eq 0) {
    throw "Specify -Skill <name>, -All, or -List."
}

foreach ($skillName in $Skill) {
    $source = Join-Path $repoRoot $skillSources[$skillName]
    $skillFile = Join-Path $source "SKILL.md"

    if (-not (Test-Path -LiteralPath $skillFile)) {
        throw "Missing SKILL.md for '$skillName' at '$source'. Run this script from a cloned CrowdSkill repository."
    }

    $destination = Join-Path $destinationRootFull $skillName
    $destinationFull = [System.IO.Path]::GetFullPath($destination)

    if (-not $destinationFull.StartsWith($destinationRootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Resolved destination escaped the destination root: $destinationFull"
    }

    if (Test-Path -LiteralPath $destinationFull) {
        Remove-Item -LiteralPath $destinationFull -Recurse -Force
    }

    Copy-Item -LiteralPath $source -Destination $destinationFull -Recurse -Force

    [PSCustomObject]@{
        Skill       = $skillName
        Source      = $source
        Destination = $destinationFull
        Status      = "Installed"
    }
}
