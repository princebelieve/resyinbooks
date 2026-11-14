$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSCommandPath))
$source = Join-Path $project 'Professor_Supplied\Supplied_Cover_Wrap.jpeg'
$output = Join-Path $project 'For_Professor\WAEC_NECO_English_Language_Cover_Wrap_Without_Testimonials_Review.jpeg'
Add-Type -AssemblyName System.Drawing
$image = [System.Drawing.Bitmap]::FromFile($source)
$graphics = [System.Drawing.Graphics]::FromImage($image)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit

$navy = [System.Drawing.Color]::FromArgb(255, 5, 19, 62)
$gold = [System.Drawing.Color]::FromArgb(255, 231, 169, 28)
$cream = [System.Drawing.Color]::FromArgb(255, 255, 248, 231)
$ink = [System.Drawing.Color]::FromArgb(255, 18, 34, 61)
$green = [System.Drawing.Color]::FromArgb(255, 25, 101, 64)
$muted = [System.Drawing.Color]::FromArgb(255, 79, 86, 94)

# Redesign the back panel from the preserved source, leaving spine and front artwork untouched.
$graphics.FillRectangle([System.Drawing.SolidBrush]::new($navy), 0, 0, 598, 820)
$graphics.FillRectangle([System.Drawing.SolidBrush]::new($cream), 20, 18, 558, 784)
$graphics.FillRectangle([System.Drawing.SolidBrush]::new($navy), 20, 18, 558, 180)
$graphics.FillRectangle([System.Drawing.SolidBrush]::new($gold), 20, 192, 558, 6)

$fontEyebrow = [System.Drawing.Font]::new('Arial', 16, [System.Drawing.FontStyle]::Bold)
$fontTitle = [System.Drawing.Font]::new('Arial', 24, [System.Drawing.FontStyle]::Bold)
$fontSub = [System.Drawing.Font]::new('Arial', 12.5, [System.Drawing.FontStyle]::Bold)
$fontBody = [System.Drawing.Font]::new('Arial', 12.2, [System.Drawing.FontStyle]::Regular)
$fontHead = [System.Drawing.Font]::new('Arial', 13, [System.Drawing.FontStyle]::Bold)
$fontBullet = [System.Drawing.Font]::new('Arial', 11.8, [System.Drawing.FontStyle]::Regular)
$fontBox = [System.Drawing.Font]::new('Arial', 11.7, [System.Drawing.FontStyle]::Bold)
$fontTag = [System.Drawing.Font]::new('Arial', 10.5, [System.Drawing.FontStyle]::Bold)
$brushGold = [System.Drawing.SolidBrush]::new($gold)
$brushWhite = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::White)
$brushInk = [System.Drawing.SolidBrush]::new($ink)
$brushGreen = [System.Drawing.SolidBrush]::new($green)
$brushMuted = [System.Drawing.SolidBrush]::new($muted)
$brushCream = [System.Drawing.SolidBrush]::new($cream)
$brushNavy = [System.Drawing.SolidBrush]::new($navy)
$goldPen = [System.Drawing.Pen]::new($gold, 2)

$graphics.DrawString('WAEC / NECO', $fontEyebrow, $brushGold, 48, 35)
$graphics.DrawString('ENGLISH LANGUAGE', $fontTitle, $brushWhite, 48, 62)
$graphics.DrawString('REVISION HANDBOOK', $fontTitle, $brushWhite, 48, 96)
$graphics.DrawString('A practical study guide for senior secondary students', $fontSub, $brushGold, 49, 151)

$graphics.DrawString('Build your English skills one step at a time.', $fontHead, $brushGreen, 46, 221)
$body = 'From grammar and vocabulary to comprehension, summary, essays and letters, this handbook explains key ideas and gives you focused practice to strengthen understanding and accuracy.'
$bodyRect = [System.Drawing.RectangleF]::new(46, 252, 482, 85)
$graphics.DrawString($body, $fontBody, $brushInk, $bodyRect)

$graphics.DrawLine($goldPen, 46, 349, 552, 349)
$graphics.DrawString('WHAT YOU WILL STUDY', $fontHead, $brushInk, 46, 365)
$bullets = @(
    'Grammar, tenses and subject-verb agreement',
    'Vocabulary, lexis, structure and idioms',
    'Comprehension and summary writing',
    'Essays, articles, speeches and letters',
    'Oral English, speech sounds and stress',
    'Figures of speech, registers and study skills'
)
$bulletY = 397
foreach ($item in $bullets) {
    $graphics.FillEllipse([System.Drawing.SolidBrush]::new($gold), 49, $bulletY + 6, 8, 8)
    $graphics.DrawString($item, $fontBullet, $brushInk, 66, $bulletY)
    $bulletY += 31
}

$box = [System.Drawing.Rectangle]::new(44, 602, 508, 86)
$graphics.FillRectangle([System.Drawing.SolidBrush]::new($navy), $box)
$graphics.DrawRectangle([System.Drawing.Pen]::new($gold, 2), $box)
$boxText = 'Includes two complete original practice examinations, with passages, questions, answer keys and a practical marking guide.'
$boxRect = [System.Drawing.RectangleF]::new(60, 615, 475, 60)
$graphics.DrawString($boxText, $fontBox, $brushWhite, $boxRect)

$graphics.DrawString('Practise with purpose. Learn from every correction.', $fontTag, $brushGreen, 46, 713)
# Leave clear space for a publisher-assigned barcode when a valid ISBN and printer template are available.
$graphics.FillRectangle([System.Drawing.SolidBrush]::new([System.Drawing.Color]::White), 425, 733, 126, 55)
$graphics.DrawRectangle([System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(255, 204, 198, 181), 1), 425, 733, 126, 55)
$graphics.FillRectangle([System.Drawing.SolidBrush]::new($gold), 0, 820, 598, 33)
$graphics.DrawString('READ. PRACTISE. COMMUNICATE.', $fontTag, $brushNavy, 190, 827)

$image.Save($output, [System.Drawing.Imaging.ImageFormat]::Jpeg)
$graphics.Dispose()
$image.Dispose()
Write-Output "Updated review wrap: $output"
