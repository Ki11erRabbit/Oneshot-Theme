
import argparse
import os
import subprocess
import sys


colors = {
        'purple': {"base": '#9664ff', "base_hover": "#6442a5", "selection": {"fill": "#261940", "border": "#4b327f"} ,"selection_hover": {"fill": "#191129", "border": "#322152"}},
        'blue': {"base": '#746BE6', "base_hover": "#3a358c", "selection": {"fill": "#1d1b39", "border": "#3a3572"} ,"selection_hover": {"fill": "#0f0d23", "border": "#1d1a46"}},
        'cyan': {"base": '#35CDD2', "base_hover": "#196f71", "selection": {"fill": "#0d3335", "border": "#1a6669"} ,"selection_hover": {"fill": "#061c1c", "border": "#0c3738"}},
        'green': {"base": '#3FD564', "base_hover": "#0a8a49", "selection": {"fill": "#103519", "border": "#1f6a32"} ,"selection_hover": {"fill": "#032312", "border": "#054524"}},
        'yellow': {"base": '#FFD26A', "base_hover": "#b37d00", "selection": {"fill": "#40351b", "border": "#7f6935"} ,"selection_hover": {"fill": "#2d1f00", "border": "#593e00"}},
        'red': {"base": '#D5216A', "base_hover": "#6a103e", "selection": {"fill": "#35081b", "border": "#6a1035"} ,"selection_hover": {"fill": "#1b0410", "border": "#35081f"}},
        'white': {"base": '#FFFFFF', "base_hover": "#808080", "selection": {"fill": "#404040", "border": "#7f7f7f"} ,"selection_hover": {"fill": "#202020", "border": "#404040"}},
        'pink': {"base": '#FE55BF', "base_hover": "#b50f77", "selection": {"fill": "#3f1530", "border": "#7e2a5f"} ,"selection_hover": {"fill": "#2d041e", "border": "#5a073b"}},
        'orange': {"base": '#FD8F4D', "base_hover": "#ca4c02", "selection": {"fill": "#3f2413", "border": "#7e4726"} ,"selection_hover": {"fill": "#331301", "border": "#652601"}},
        }
#todo: add remaining colors

output_dir = "oneshot_theme"
src_dir = "src"
cwd = os.getcwd()


def convert_assets(file, output_dir, color):
    base = colors[color]["base"]
    base_hover = colors[color]["base_hover"]
    dark = colors[color]["selection_hover"]["border"]
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
        # Change colors from light grey to base_hover
        sed_command = ['sed', '-i', f's/rgb(90.196078%, 90.196078%, 90.196078%)/{base_hover}/g', f'{output_dir}/assets/{asset}']
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
    base_hover = colors[color]["base_hover"]
    selection_fill = colors[color]["selection"]["fill"]
    selection_border = colors[color]["selection"]["border"]
    selection_hover_fill = colors[color]["selection_hover"]["fill"]
    selection_hover_border = colors[color]["selection_hover"]["border"]

    stylesheet_path = f"{cwd}/{src_dir}/{file}/sass/_colors.scss"

    with open(stylesheet_path, 'w') as file:
        file.write(f"""$fg_color: {base}
$bg_color: #000000
$hover_fg_color: {base_hover}
$insensitive_fg_color: {selection_hover_border}
$insensitive_bg_color: {selection_hover_fill}
$selected_fg_color: {selection_border}
$selected_bg_color: {selection_fill}
""")
    

def output_file(file, color):
    out_dir = f"{cwd}/{output_dir}/{file}"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    convert_assets(file, out_dir, color)
    generate_colors_stylesheet(file, color)
    program = [f'{cwd}/{src_dir}/{file}/parse-sass.sh', f'{out_dir}/gtk.css']
    proc = subprocess.Popen(program)
    proc.wait()

def create_index_theme(color):
    with open(f"{cwd}/{output_dir}/index.theme", 'w') as file:
        file.write(f"""[Desktop Entry]
Type=X-GNOME-Metatheme
Name=Oneshot Theme {color.capitalize()}
Comment=A Linux theme inspired by the UI in Oneshot: World Machine Edition
Encoding=UTF-8

[X-GNOME-Metatheme]
GtkTheme=Oneshot-{color}
MetacityTheme=Oneshot-{color}
IconTheme=oneshot_icons
CursorTheme=oneshot_icons
""")

def main(color):
    if color == "user":
        if args.color_base == None or args.color_base_hover == None or args.color_dark == None or args.color_selection_fill == None or args.color_selection_border == None or args.color_selection_hover_fill == None or args.color_selection_hover_border == None:
            print("Please provide all color options for a custom color")
            sys.exit(1)
        colors["user"] = {"base": args.color_base, "base_hover": args.color_selected, "dark": args.color_dark}
        color = "user"
    
    for file in os.listdir(src_dir):
        if file == 'gtk-3.0': #or file == 'gtk-4.0':
            output_file(file, color)
    
    create_index_theme(color)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate oneshot themes')
    parser.add_argument('-c','--color', type=str, help='Color of the theme. Set to "user" and set the other color options to use a custom color', default='purple')
    parser.add_argument('-cb','--color-base', type=str, help='Base Color of the theme', default=None)
    parser.add_argument('-ch','--color-base-hover', type=str, help='Base Hover Color of the theme', default=None)
    parser.add_argument('-csf','--color-selection-fill', type=str, help='Selection Fill Color of the theme', default=None)
    parser.add_argument('-csb','--color-selection-border', type=str, help='Selection Border Color of the theme', default=None)
    parser.add_argument('-cshf','--color-selection-hover-fill', type=str, help='Selection Hover Fill Color of the theme', default=None)
    parser.add_argument('-cshb','--color-selection-hover-border', type=str, help='Selection Hover Border Color of the theme', default=None)
    args = parser.parse_args()
    main(args.color)
