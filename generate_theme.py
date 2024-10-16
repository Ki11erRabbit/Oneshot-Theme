
import argparse
import os
import subprocess
import sys


colors = {
        'purple': {"base": '#9664ff', "selected": "#6442a5", "dark": "#371b78"},
        'blue': {"base": '#746BE6', "selected": "#3a358c", "dark": "#29287c"},
        'cyan': {"base": '#35CDD2', "selected": "#196f71", "dark": "#056567"},
        'green': {"base": '#3FD564', "selected": "#0a8a49", "dark": "#007f3f"},
        'yellow': {"base": '#FFD26A', "selected": "#b37d00", "dark": "#a77300"},
        'red': {"base": '#D5216A', "selected": "#6a103e", "dark": "#5f0135"},
        'white': {"base": '#FFFFFF', "selected": "#808080", "dark": "#767676"},
        'pink': {"base": '#FE55BF', "selected": "#b50f77", "dark": "#a9006d"},
        'orange': {"base": '#FD8F4D', "selected": "#ca4c02", "dark": "#be4100"},
        }
#todo: add remaining colors

output_dir = "oneshot_theme"
src_dir = "src"
cwd = os.getcwd()


def convert_assets(file, output_dir, color):
    base = colors[color]["base"]
    selected = colors[color]["selected"]
    dark = colors[color]["dark"]
    if not os.path.exists(f"{output_dir}/assets"):
        os.makedirs(f"{output_dir}/assets")
    if not os.path.exists(f"{output_dir}/assets/scalable"):
        os.makedirs(f"{output_dir}/assets/scalable")
    
    for asset in os.listdir(f"{cwd}/{src_dir}/{file}/assets"):
        if not asset.endswith(".svg"):
            continue
        # scale up svg to 512px
        program = ['rsvg-convert', '-a', '-w', '512', '-f', 'svg', '-o', f'{output_dir}/assets/{asset}', f'{cwd}/{src_dir}/{file}/assets/{asset}']
        proc = subprocess.Popen(program)
        proc.wait()

        # change colors to match theme
        # Change colors from white to base
        sed_command = ['sed', '-i', f's/rgb(100%, 100%, 100%)/{base}/g', f'{output_dir}/assets/{asset}']
        proc = subprocess.Popen(sed_command, cwd=f'{output_dir}/assets')
        proc.wait()
        # Change colors from light grey to selected
        sed_command = ['sed', '-i', f's/rgb(90.196078%, 90.196078%, 90.196078%)/{selected}/g', f'{output_dir}/assets/{asset}']
        proc = subprocess.Popen(sed_command, cwd=f'{output_dir}/assets')
        proc.wait()
        # Change colors from dark grey to dark
        sed_command = ['sed', '-i', f's/rgb(50.196078%, 50.196078%, 50.196078%)/{dark}/g', f'{output_dir}/assets/{asset}']
        proc = subprocess.Popen(sed_command, cwd=f'{output_dir}/assets')
        proc.wait()
        
        asset_name = os.path.splitext(asset)[0]

        png_convert = ['rsvg-convert', '-a', '-w', '512', '-f', 'png', '-o', f'{output_dir}/assets/{asset_name}.png', f'{output_dir}/assets/{asset}']
        proc = subprocess.Popen(png_convert)
        proc.wait()
        os.rename(f'{output_dir}/assets/{asset}', f'{output_dir}/assets/scalable/{asset}')


def generate_colors_stylesheet(file, color):
    base = colors[color]["base"]
    selected = colors[color]["selected"]
    dark = colors[color]["dark"]

    stylesheet_path = f"{cwd}/{src_dir}/{file}/sass/_colors.scss"

    with open(stylesheet_path, 'w') as file:
        file.write(f"$fg_color: {base}\n$selected_fg_color: {selected}\n$insensitive_fg_color: {dark}\n$bg_color: #000000\n")
    

def output_file(file, color):
    out_dir = f"{cwd}/{output_dir}/{file}"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    convert_assets(file, out_dir, color)
    generate_colors_stylesheet(file, color)
    program = [f'{cwd}/{src_dir}/{file}/parse-sass.sh', f'{out_dir}/gtk.css']
    proc = subprocess.Popen(program)
    proc.wait()


def main(color):
    if color == "user":
        if args.color_base == None or args.color_selected == None or args.color_dark == None:
            print("Please provide all color options for a custom color")
            sys.exit(1)
        colors["user"] = {"base": args.color_base, "selected": args.color_selected, "dark": args.color_dark}
        color = "user"
    
    for file in os.listdir(src_dir):
        if file == 'gtk-3.0': #or file == 'gtk-4.0':
            output_file(file, color)
    



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate oneshot themes')
    parser.add_argument('-c','--color', type=str, help='Color of the theme. Set to "user" and set the other color options to use a custom color', default='purple')
    parser.add_argument('-cb','--color-base', type=str, help='Base Color of the theme', default=None)
    parser.add_argument('-cs','--color-selected', type=str, help='Selected Color of the theme', default=None)
    parser.add_argument('-cd','--color-dark', type=str, help='Dark Color of the theme', default=None)
    args = parser.parse_args()
    main(args.color)
