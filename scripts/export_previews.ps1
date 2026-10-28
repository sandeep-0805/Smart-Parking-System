try {
    $p = New-Object -ComObject PowerPoint.Application
    $pres = $p.Presentations.Open('C:\Users\sande\Downloads\SmartTraffic\SmartParking_Presentation.pptx', [Microsoft.Office.Core.MsoTriState]::msoTrue, [Microsoft.Office.Core.MsoTriState]::msoFalse, [Microsoft.Office.Core.MsoTriState]::msoFalse)
    for ($i = 1; $i -le $pres.Slides.Count; $i++) {
        $num = "{0:D2}" -f $i
        $pres.Slides.Item($i).Export("C:\Users\sande\Downloads\SmartTraffic\screenshots\slide_$num.png", 'PNG', 1920, 1080)
    }
    $pres.Close()
    $p.Quit()
    Write-Host "SUCCESS: Exported all 30 slide previews!"
} catch {
    Write-Host "PowerPoint export failed: $_"
}
