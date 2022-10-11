<html>
<body>
<?php

function showImagesInDir($dir)
{
    $files = scandir($dir);
    $ext = '.png';
    
    foreach ($files as $ele)
    {
        //if (is_dir($ele))
        //{
        //    showImagesInDir($ele);
        //}
        //elseif (substr_compare($ele, $ext, -strlen($ext), strlen($ext)) === 0)
        if (substr_compare($ele, $ext, -strlen($ext), strlen($ext)) === 0)
        {
            //echo "$ele\n";
            echo "<img src=$ele>";
        }
    }
}

$dir = dirname(__FILE__);
//echo "$dir\n";

showImagesInDir($dir);

?>
</body>
</html>
