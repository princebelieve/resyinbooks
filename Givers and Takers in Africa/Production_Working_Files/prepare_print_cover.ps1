$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$base = Split-Path -Parent $MyInvocation.MyCommand.Path
$inputFile = Join-Path $base 'Source_Materials\Givers and Takers Book Cover.jpeg'
$outputDir = Join-Path $base 'Production'
$pageCount = 167
$dpi = 300
$trimWidthIn = 420.0 / 72.0
$trimHeightIn = 594.96 / 72.0
$spineWidthIn = $pageCount * 0.0025 # same cream-paper assumption used for the reference book's cover
$trimWidthPx = [int][Math]::Round($trimWidthIn * $dpi)
$trimHeightPx = [int][Math]::Round($trimHeightIn * $dpi)
$spineWidthPx = [int][Math]::Round($spineWidthIn * $dpi)
$bleedPx = [int][Math]::Round(0.125 * $dpi)
$totalWidthPx = 2 * $trimWidthPx + $spineWidthPx + 2 * $bleedPx
$totalHeightPx = $trimHeightPx + 2 * $bleedPx
# The panel artwork extends through the outside bleed. This maps to 3701 x 2555 px for this edition.
$backWidthPx = $trimWidthPx + $bleedPx
$backPanelRight = $bleedPx + $trimWidthPx
$frontPanelLeft = $backPanelRight + $spineWidthPx
$frontWidthPx = $totalWidthPx - $frontPanelLeft
$backScaleX = $backWidthPx / 541.0
$spreadScaleY = $totalHeightPx / 853.0

$source = [System.Drawing.Bitmap]::FromFile($inputFile)
try {
    if ($source.Width -ne 1280 -or $source.Height -ne 853) { throw "Unexpected source wrap dimensions: $($source.Width)x$($source.Height)" }
    $cover = New-Object System.Drawing.Bitmap($totalWidthPx,$totalHeightPx,[System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
    $cover.SetResolution($dpi,$dpi)
    try {
        $g = [System.Drawing.Graphics]::FromImage($cover)
        try {
            $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
            $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
            $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
            $g.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
            $g.DrawImage($source,[System.Drawing.Rectangle]::new(0,0,$backPanelRight,$totalHeightPx),[System.Drawing.Rectangle]::new(0,0,541,853),[System.Drawing.GraphicsUnit]::Pixel)
            $g.DrawImage($source,[System.Drawing.Rectangle]::new($frontPanelLeft,0,$frontWidthPx,$totalHeightPx),[System.Drawing.Rectangle]::new(680,0,600,853),[System.Drawing.GraphicsUnit]::Pixel)

            # Keep the ISBN/barcode proportions while covering the horizontally stretched copy beneath it.
            $boxX = [int][Math]::Round(330 * $backScaleX)
            $boxY = [int][Math]::Round(666 * $spreadScaleY)
            $boxW = [int][Math]::Round(190 * $backScaleX)
            $boxH = [int][Math]::Round(142 * $spreadScaleY)
            $white = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
            try { $g.FillRectangle($white,$boxX,$boxY,$boxW,$boxH) } finally { $white.Dispose() }
            $isbnPanel = $source.Clone([System.Drawing.Rectangle]::new(330,666,190,142),[System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
            try {
                $barcodeW = [int][Math]::Round(190 * $spreadScaleY)
                $barcodeH = [int][Math]::Round(142 * $spreadScaleY)
                $barcodeX = $boxX + [int][Math]::Round(($boxW-$barcodeW)/2)
                $g.DrawImage($isbnPanel,[System.Drawing.Rectangle]::new($barcodeX,$boxY,$barcodeW,$barcodeH))
            } finally { $isbnPanel.Dispose() }

            $green = [System.Drawing.Color]::FromArgb(6,59,31)
            $gold = [System.Drawing.Color]::FromArgb(226,188,73)
            $spineX = $backPanelRight
            $spineBrush = New-Object System.Drawing.SolidBrush($green)
            try { $g.FillRectangle($spineBrush,$spineX,0,$spineWidthPx,$totalHeightPx) } finally { $spineBrush.Dispose() }
            $linePen = New-Object System.Drawing.Pen($gold,2)
            try {
                foreach ($x in @([int]($spineX+4),[int]($spineX+9),[int]($spineX+$spineWidthPx-10),[int]($spineX+$spineWidthPx-5))) { $g.DrawLine($linePen,$x,0,$x,$totalHeightPx) }
            } finally { $linePen.Dispose() }

            function Draw-SpineText($graphics,$x,$value,$font,$color) {
                $state=$graphics.Save()
                try {
                    $graphics.TranslateTransform([single]$x,[single]1277.5)
                    $graphics.RotateTransform(90)
                    $format=New-Object System.Drawing.StringFormat
                    try {
                        $format.Alignment=[System.Drawing.StringAlignment]::Center
                        $format.LineAlignment=[System.Drawing.StringAlignment]::Center
                        $size=$graphics.MeasureString($value,$font)
                        $rect=[System.Drawing.RectangleF]::new(-$size.Width/2,-$size.Height/2,$size.Width,$size.Height)
                        $brush=New-Object System.Drawing.SolidBrush($color)
                        try { $graphics.DrawString($value,$font,$brush,$rect,$format) } finally { $brush.Dispose() }
                    } finally { $format.Dispose() }
                } finally { $graphics.Restore($state) }
            }
            $g.TextRenderingHint=[System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
            $fontTitle=New-Object System.Drawing.Font('Georgia',8,[System.Drawing.FontStyle]::Bold,[System.Drawing.GraphicsUnit]::Point)
            $fontSubtitle=New-Object System.Drawing.Font('Georgia',5.3,[System.Drawing.FontStyle]::Regular,[System.Drawing.GraphicsUnit]::Point)
            $fontAuthor=New-Object System.Drawing.Font('Georgia',5.8,[System.Drawing.FontStyle]::Bold,[System.Drawing.GraphicsUnit]::Point)
            try {
                $centerX=$spineX+$spineWidthPx/2
                Draw-SpineText $g ($centerX-27) 'GIVERS AND TAKERS IN AFRICA' $fontTitle $gold
                Draw-SpineText $g $centerX 'THE POLITICS OF SELF-INTEREST, GENEROSITY, LEADERSHIP AND SUSTAINABLE DEVELOPMENT' $fontSubtitle ([System.Drawing.Color]::White)
                Draw-SpineText $g ($centerX+26) 'PROF. JOHNSON AGHARESE EGONMWAN' $fontAuthor $gold
            } finally { $fontTitle.Dispose(); $fontSubtitle.Dispose(); $fontAuthor.Dispose() }
        } finally { $g.Dispose() }
        $jpeg=[System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object MimeType -eq 'image/jpeg' | Select-Object -First 1
        $params=New-Object System.Drawing.Imaging.EncoderParameters(1)
        $params.Param[0]=New-Object System.Drawing.Imaging.EncoderParameter([System.Drawing.Imaging.Encoder]::Quality,[long]100)
        try {
            $output=Join-Path $outputDir 'Cover_Spread_A5_167p_Cream_Assumption.jpg'
            $cover.Save($output,$jpeg,$params)
            Write-Output "Created $output; $totalWidthPx x $totalHeightPx pixels at $dpi DPI; trim A5; $pageCount pages; $spine $spineWidthIn in cream-paper assumption."
        } finally { $params.Dispose() }
    } finally { $cover.Dispose() }
} finally { $source.Dispose() }
