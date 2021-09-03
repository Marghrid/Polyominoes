webpage_style = r"""body {
  margin: auto;
  /*background: white;*/
  font-family: sans-serif;
  color: rgba(0, 0, 0, .8);
  line-height: 1.8em;
  padding: 1%;
  text-align: center;
}

@media (orientation: landscape) {
  body {
    max-width: 70em;
  }
}

@media (prefers-color-scheme: dark) {
  body {
    background-color: #222;
    color: rgba(255, 255, 255, 0.8);
  }

  a {
    color: rgba(255, 255, 255, 0.65) !important;
    text-decoration: none !important;
  }

  a:hover {
    color: rgba(255, 255, 255, 0.8) !important;
  }
  #intro_img_planets,
  #intro_img_house {
      background-image: none !important;
      padding: 10% 1% 3% !important;
  }
}

@media (min-width: 768px) {
  body {
    width: 70%;
  }
}

a {
    color: rgba(0, 0, 0, .55);
    text-decoration: none;
}
a:hover {
    color: rgba(0, 0, 0, .6);
}

.img-container {
  display: flex;
  flex-wrap: wrap;
  flex-direction: row;
  justify-content: center;
}

.img-container a {
  flex-grow: 1;
}

.img-container img {
    margin: 5%;
  max-height: 100%;
  min-width: 100px;
  max-width: 300px;
  object-fit: cover;
  vertical-align: bottom;
}

#projects article video,
#projects article image,
#projects article a.image {
    width: 60%;
    margin: 0 auto;
    display: block;
}

#projects article h3 {
    margin-bottom: 0;
}

#projects article h4 {
    margin-top: 0;
}

.icons a {
    color: rgba(0, 0, 0, .55);
    text-decoration: none;
}

.icons a:hover {
    color: rgba(0, 0, 0, .6);
}

ul.icons {
        cursor: default;
        list-style: none;
        padding-left: 0;
    }

        ul.icons li {
            display: inline-block;
            padding: 0 1em 0 0;
            font-size: 120%;
            font-weight: bold;
        }

            ul.icons li:last-child {
                padding-right: 0 !important;
            }

            ul.icons li .icon:before {
                font-size: 1.25em;
            }

        ul.icons li span{
            display: inline-block;
            padding: 0 1em 0 .5em;
            font-size: 80%;
            font-family: Merriweather, sans-serif;
            font-weight: normal;
        }


footer {
    text-align: center;
}

footer .icons {
    font-size: 120%;
}

span.smallcaps {
    font-variant: small-caps;
}
"""

webpage_index = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <title>Polyominoes</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" type="text/css" href="style.css" />
  <meta name="theme-color" content="#ffffff">
</head>

<body>
  <?php
    $dir   = "./";
    $files = scandir($dir);
    $files = array_diff(($files), array('.', '..', "style.css", "index.php"));
    $files = array_values($files);
    $json = json_encode($files);
    $num = count($files);
    echo "<h1>{$num} configurations </h1>";
  ?>

  <section>
    <div class=img-container id=xoxo-configs>
      <!-- <?php
        $chunks = array_chunk($files,21);
        $first_chunk = $chunks[0];
        print_r($first_chunk);
        foreach($first_chunk as $file) {
          echo "<p>{$file}</p>";
          echo "<a href=\"{$dir}{$file}\"><img src=\"{$dir}{$file}\"></a>";
        }
      ?> -->
    </div>
    <p id=info-text>DUMMYTEXT</p>
    <button type="button" onclick="load_some_more()">Load more</button>
  </section>

<script>
    show_num = 24
    function load_some_more() {
      let data = <?php echo $json; ?>;
      
      if( typeof load_some_more.counter == 'undefined' ) {
          load_some_more.counter = 0;
      } else {
        load_some_more.counter++;
      }
      div = document.getElementById('xoxo-configs');
      for (let i = load_some_more.counter*show_num; 
        i < (load_some_more.counter+1)*show_num && i < data.length; 
        ++i) {
        var a = document.createElement('a');
        var img = document.createElement('img');
        img.src = "" + data[i];
        a.appendChild(img);
        a.href = "" + data[i];
        div.appendChild(a);
      }
      p = document.getElementById("info-text");
      // todo: disable/remove "load more" button
      let num_configs = Math.min((load_some_more.counter+1)*show_num, data.length)
      p.innerHTML=`Showing ${num_configs} out of ${data.length} configurations.`;
    }
    load_some_more();
    console.log("Go away. Console is not for you.");
</script>
</body>
</html>
"""
