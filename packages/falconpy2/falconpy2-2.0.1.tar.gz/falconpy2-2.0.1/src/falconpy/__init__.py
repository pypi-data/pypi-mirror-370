from ._hal import (
    import_as,
    install,
    uninstall,
    HALModuleProxy,
    HALWrapper,
    hal_wrap,
)

# Create mock classes for CrowdStrike FalconPy imports
class _MockClass:
    """Base mock class that blocks all method calls"""
    def __init__(self, name="MockClass"):
        self._name = name
    
    def __getattr__(self, name):
        return hal_wrap(lambda *args, **kwargs: None)
    
    def __call__(self, *args, **kwargs):
        print("I'm sorry Dave, I'm afraid I can't do that.")
        return None
    
    def __repr__(self):
        return f"<Mock {self._name}>"

# All CrowdStrike FalconPy classes
Alerts = _MockClass("Alerts")
APIHarness = _MockClass("APIHarness")
APIHarnessV2 = _MockClass("APIHarnessV2")
APIIntegrations = _MockClass("APIIntegrations")
ASPM = _MockClass("ASPM")
CAOHunting = _MockClass("CAOHunting")
CertificateBasedExclusions = _MockClass("CertificateBasedExclusions")
CloudAWSRegistration = _MockClass("CloudAWSRegistration")
CloudAzureRegistration = _MockClass("CloudAzureRegistration")
CloudOCIRegistration = _MockClass("CloudOCIRegistration")
CloudConnectAWS = _MockClass("CloudConnectAWS")
CloudSecurityAssets = _MockClass("CloudSecurityAssets")
CloudSnapshots = _MockClass("CloudSnapshots")
ConfigurationAssessment = _MockClass("ConfigurationAssessment")
ConfigurationAssessmentEvaluationLogic = _MockClass("ConfigurationAssessmentEvaluationLogic")
ContainerAlerts = _MockClass("ContainerAlerts")
ContainerDetections = _MockClass("ContainerDetections")
ContainerImages = _MockClass("ContainerImages")
ContainerPackages = _MockClass("ContainerPackages")
ContainerVulnerabilities = _MockClass("ContainerVulnerabilities")
CSPMRegistration = _MockClass("CSPMRegistration")
CustomIOA = _MockClass("CustomIOA")
CustomStorage = _MockClass("CustomStorage")
D4CRegistration = _MockClass("D4CRegistration")
Detects = _MockClass("Detects")
DeviceControlPolicies = _MockClass("DeviceControlPolicies")
Discover = _MockClass("Discover")
DriftIndicators = _MockClass("DriftIndicators")
EventStreams = _MockClass("EventStreams")
ExposureManagement = _MockClass("ExposureManagement")
FalconCompleteDashboard = _MockClass("FalconCompleteDashboard")
FalconContainer = _MockClass("FalconContainer")
FalconXSandbox = _MockClass("FalconXSandbox")
FDR = _MockClass("FDR")
FileVantage = _MockClass("FileVantage")
FirewallManagement = _MockClass("FirewallManagement")
FirewallPolicies = _MockClass("FirewallPolicies")
FlightControl = _MockClass("FlightControl")
FoundryLogScale = _MockClass("FoundryLogScale")
HostGroup = _MockClass("HostGroup")
Hosts = _MockClass("Hosts")
IdentityProtection = _MockClass("IdentityProtection")
ImageAssessmentPolicies = _MockClass("ImageAssessmentPolicies")
Incidents = _MockClass("Incidents")
InstallationTokens = _MockClass("InstallationTokens")
Intel = _MockClass("Intel")
IOAExclusions = _MockClass("IOAExclusions")
IOC = _MockClass("IOC")
IOCs = _MockClass("IOCs")
KubernetesProtection = _MockClass("KubernetesProtection")
MalQuery = _MockClass("MalQuery")
MessageCenter = _MockClass("MessageCenter")
MLExclusions = _MockClass("MLExclusions")
MobileEnrollment = _MockClass("MobileEnrollment")
OAuth2 = _MockClass("OAuth2")
ODS = _MockClass("ODS")
OverwatchDashboard = _MockClass("OverwatchDashboard")
PreventionPolicy = _MockClass("PreventionPolicy")
Quarantine = _MockClass("Quarantine")
QuickScan = _MockClass("QuickScan")
RealTimeResponseAdmin = _MockClass("RealTimeResponseAdmin")
RealTimeResponse = _MockClass("RealTimeResponse")
RealTimeResponseAudit = _MockClass("RealTimeResponseAudit")
Recon = _MockClass("Recon")
ReportExecutions = _MockClass("ReportExecutions")
ResponsePolicies = _MockClass("ResponsePolicies")
SampleUploads = _MockClass("SampleUploads")
ScheduledReports = _MockClass("ScheduledReports")
SensorDownload = _MockClass("SensorDownload")
SensorUpdatePolicy = _MockClass("SensorUpdatePolicy")
SensorVisibilityExclusions = _MockClass("SensorVisibilityExclusions")
SpotlightEvaluationLogic = _MockClass("SpotlightEvaluationLogic")
SpotlightVulnerabilities = _MockClass("SpotlightVulnerabilities")
TailoredIntelligence = _MockClass("TailoredIntelligence")
ThreatGraph = _MockClass("ThreatGraph")
UnidentifiedContainers = _MockClass("UnidentifiedContainers")
UserManagement = _MockClass("UserManagement")
Workflows = _MockClass("Workflows")
ZeroTrustAssessment = _MockClass("ZeroTrustAssessment")

__all__ = [
    "import_as", "install", "uninstall", "HALModuleProxy", "HALWrapper",
    "Alerts", "APIHarness", "APIHarnessV2", "APIIntegrations", "ASPM", "CAOHunting", "CertificateBasedExclusions",
    "CloudAWSRegistration", "CloudAzureRegistration", "CloudOCIRegistration", "CloudConnectAWS",
    "CloudSecurityAssets", "CloudSnapshots", "ConfigurationAssessment", "ConfigurationAssessmentEvaluationLogic",
    "ContainerAlerts", "ContainerDetections", "ContainerImages", "ContainerPackages", "ContainerVulnerabilities",
    "CSPMRegistration", "CustomIOA", "CustomStorage", "D4CRegistration", "Detects", "DeviceControlPolicies",
    "Discover", "DriftIndicators", "EventStreams", "ExposureManagement", "FalconCompleteDashboard",
    "FalconContainer", "FalconXSandbox", "FDR", "FileVantage", "FirewallManagement", "FirewallPolicies",
    "FlightControl", "FoundryLogScale", "HostGroup", "Hosts", "IdentityProtection", "ImageAssessmentPolicies",
    "Incidents", "InstallationTokens", "Intel", "IOAExclusions", "IOC", "IOCs", "KubernetesProtection",
    "MalQuery", "MessageCenter", "MLExclusions", "MobileEnrollment", "OAuth2", "ODS", "OverwatchDashboard",
    "PreventionPolicy", "Quarantine", "QuickScan", "RealTimeResponseAdmin", "RealTimeResponse",
    "RealTimeResponseAudit", "Recon", "ReportExecutions", "ResponsePolicies", "SampleUploads",
    "ScheduledReports", "SensorDownload", "SensorUpdatePolicy", "SensorVisibilityExclusions",
    "SpotlightEvaluationLogic", "SpotlightVulnerabilities", "TailoredIntelligence", "ThreatGraph",
    "UnidentifiedContainers", "UserManagement", "Workflows", "ZeroTrustAssessment"
]
