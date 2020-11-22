<#
    .SYNOPSIS
        This script gets information of all azure resources in a subscription.
	
	.DESCRIPTION
		This script gets the following information of all azure resources in a subscription: id,name,location,changedTime,createdTime,kind,type.
		It stores the information in csv files one per resorce group. The files are zipped in a folder called azureResources_ yyyyMMdd_HHmmss and uploaded to a container in an azure storage account.
#>

param (
	# Name of an azure storage account where the zipped folder with csv file is going to be stored. 
	[string]$storage = "teststorage", 
	# Name of an azure container in the storage account where the zipped folder with csv file is going to be stored
	[string]$container = "testcontainer", 
	[switch]$verbose = $false
)
$dateTime = Get-Date -Format "yyyyMMdd_HHmmss"

function Check-AzErrors{
	$azError = $args[0] | Select-String -Pattern "error"
	if($azError){
		throw $azError
	}
}

try{

	Add-Type -assembly "system.io.compression.filesystem"
	if($verbose){
		$VerbosePreference = "continue"
	}
	Write-Verbose "Getting resource group names"
	$resourceGroupList = $(az group list --query [].name --output tsv) 2>&1
	Check-AzErrors $resourceGroupList
	Write-Verbose "Getting storage key"
	$storageKey  =  $( az storage account keys list --account-name $storage --query [0].value -o tsv) 2>&1
	Check-AzErrors $storageKey

	Write-Verbose "Creating local directory"
	$dirName = "azureResources_$($dateTime)"
	mkdir $dirName
	$fullDirPath = Resolve-Path $dirName 
	
	foreach($group in $resourceGroupList){
		Write-Verbose "Getting resources from group named: $($group)"
		$path = "$($dirName)\$($group)_$($dateTime).csv"
		$resourcesPerGroup = $(az resource list --resource-group $group --query "[].[id,name,location,changedTime,createdTime,kind,type]" --output tsv) 2>&1 
		if($resourcesPerGroup.Count -gt 0){
			if($resourcesPerGroup.Count -eq 1){
				Check-AzErrors $resourcesPerGroup
			}
			$resourceArray = @()
			foreach($resource in $resourcesPerGroup) {
				$propertiesArray = $resource.Split("`t")
				$resourceDetails = [PSCustomObject]@{    
						Id = $propertiesArray[0]
						Name     = $propertiesArray[1]             
						Location = $propertiesArray[2]                 
						ChangedTime = $propertiesArray[3]
						CreatedTime = $propertiesArray[4]
						Kind =  $propertiesArray[5]
						ResourceType = $propertiesArray[6]
				} 
				$resourceArray += $resourceDetails
			}
			Write-Verbose "Export resource details to a csv file"
			$resourceArray | Export-Csv -NoTypeInformation -Path $path 
		}
	}
	Write-Verbose "Creating a zip directory"
	[io.compression.zipfile]::CreateFromDirectory($fullDirPath , "$($fullDirPath).zip")
	rm -r $fullDirPath
	Write-Verbose "Uploading zip directory to the storage account"
	$uploadResult = az storage blob upload --container-name $container --file "$($fullDirPath).zip" --name "$($dirName).zip" --account-key $storageKey --account-name $storage 2>&1
	Check-AzErrors $uploadResult
	rm -r "$($fullDirPath).zip" 
	Write-Host "Zip file succesfully created and uploaded to the storage account"

} 
catch{
	Write-Host "$($dateTime): Error Message: $($error[0].Exception.Message) Line number: $($error[0].InvocationInfo.ScriptLineNumber). Invocation line: $($error[0].InvocationInfo.Line)"
}



