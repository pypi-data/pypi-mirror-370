"""Automatically checks for updates of selected packages"""

# - <https://specifications.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html>
icon = 'system-software-update'
# The label and the tooltip are used to create the default action, which is
# insert into the menu and/ or toolbar (or neither)
label = "Updates available"
tooltip = "Click to see available updates"
toolbar = {
    "index": -1,
    "separator_before": True,
    "separator_after": False
}
settings = {
    'updater_prereleases': False
}
modes = ["ide", "default"]
priority = -1000
