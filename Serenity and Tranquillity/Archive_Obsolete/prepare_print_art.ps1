$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$sourcePath = 'C:\Users\ASUS\Downloads\Serenity and Tranquillity Book Cover Spread.png'
$outDir = Join-Path (Get-Location) 'Book_Production'
$source = [System.Drawing.Bitmap]::FromFile($sourcePath)
try {
    if ($source.Width -ne 1536 -or $source.Height -ne 1024) { throw "Unexpected cover source dimensions: $($source.Width)x$($source.Height)" }
    $jpeg = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object MimeType -eq 'image/jpeg' | Select-Object -First 1
    $enc = [System.Drawing.Imaging.Encoder]::Quality
    $params = New-Object System.Drawing.Imaging.EncoderParameters(1)
    $params.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter($enc,[long]100)

    # A5 leaves at the reference PDF's landscape A4 spread size; 0.7475 in cream-paper spine assumption.
    $dpi = 300
    $pageWidthIn = (2 * 5.8472) + 0.7475 + 0.25
    $pageHeightIn = 8.268 + 0.25
    $totalW = [int][Math]::Round($pageWidthIn * $dpi)
    $totalH = [int][Math]::Round($pageHeightIn * $dpi)
    $bleed = [int][Math]::Round(0.125 * $dpi)
    $trimW = $totalW - 2 * $bleed
    $trimH = $totalH - 2 * $bleed

    $spread = New-Object System.Drawing.Bitmap($totalW,$totalH,[System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
    $spread.SetResolution($dpi,$dpi)
    $g = [System.Drawing.Graphics]::FromImage($spread)
    try {
        $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
        $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
        $g.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
        $g.DrawImage($source,[System.Drawing.Rectangle]::new($bleed,$bleed,$trimW,$trimH),[System.Drawing.Rectangle]::new(0,0,$source.Width,$source.Height),[System.Drawing.GraphicsUnit]::Pixel)
        # Extend the source edges into bleed; the original cover artwork and text remain intact.
        $g.DrawImage($source,[System.Drawing.Rectangle]::new($bleed,0,$trimW,$bleed),[System.Drawing.Rectangle]::new(0,0,$source.Width,1),[System.Drawing.GraphicsUnit]::Pixel)
        $g.DrawImage($source,[System.Drawing.Rectangle]::new($bleed,$bleed+$trimH,$trimW,$bleed),[System.Drawing.Rectangle]::new(0,$source.Height-1,$source.Width,1),[System.Drawing.GraphicsUnit]::Pixel)
        $g.DrawImage($source,[System.Drawing.Rectangle]::new(0,$bleed,$bleed,$trimH),[System.Drawing.Rectangle]::new(0,0,1,$source.Height),[System.Drawing.GraphicsUnit]::Pixel)
        $g.DrawImage($source,[System.Drawing.Rectangle]::new($bleed+$trimW,$bleed,$bleed,$trimH),[System.Drawing.Rectangle]::new($source.Width-1,0,1,$source.Height),[System.Drawing.GraphicsUnit]::Pixel)
        $corners = @(
            @{X=0; Y=0; SX=0; SY=0},
            @{X=($totalW-$bleed); Y=0; SX=($source.Width-1); SY=0},
            @{X=0; Y=($totalH-$bleed); SX=0; SY=($source.Height-1)},
            @{X=($totalW-$bleed); Y=($totalH-$bleed); SX=($source.Width-1); SY=($source.Height-1)}
        )
        foreach($corner in $corners) {
            $color = $source.GetPixel([int]$corner.SX,[int]$corner.SY)
            $brush = New-Object System.Drawing.SolidBrush($color)
            try { $g.FillRectangle($brush,[int]$corner.X,[int]$corner.Y,$bleed,$bleed) } finally { $brush.Dispose() }
        }
    } finally { $g.Dispose() }
    $spread.Save((Join-Path $outDir 'Cover_Spread_From_Original_A5_299p.jpg'),$jpeg,$params)
    $spread.Dispose()

    # Retailer marketing image: front panel only, cropped from the supplied illustrated spread.
    $front = New-Object System.Drawing.Bitmap(1800,2520,[System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
    $front.SetResolution($dpi,$dpi)
    $fg = [System.Drawing.Graphics]::FromImage($front)
    try {
        $fg.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
        $fg.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
        $fg.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
        $fg.DrawImage($source,[System.Drawing.Rectangle]::new(0,0,1800,2520),[System.Drawing.Rectangle]::new(806,0,730,1024),[System.Drawing.GraphicsUnit]::Pixel)
    } finally { $fg.Dispose() }
    $front.Save((Join-Path $outDir 'Cover_Front_OnlineStore_From_Original.jpg'),$jpeg,$params)
    $front.Dispose()
    $params.Dispose()
    Write-Output "Created A5 cover spread image $($totalW)x$($totalH) pixels at 300 DPI metadata."
    Write-Output 'Created front-only bookstore cover image 1800x2520 pixels.'
} finally { $source.Dispose() }
