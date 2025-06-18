import subprocess
import os



def run_uw_images_to_pdf(configs):
    """
    Run uw_images_to_pdf.py with different configurations.
    :param configs: List of dictionaries containing configurations.
    """
    script_path = os.path.dirname(__file__) + "/uw_images_to_pdf.py"

    for i, config in enumerate(configs, 1):
        print(f"Running configuration {i}/{len(configs)}...")
        command = [
            "python",
            script_path,
            config["url"],
            "--output",
            config["output"],
            "--format",
            config["format"],
        ]
        if "width" in config:
            command.extend(
                [
                    "--width",
                    str(config["width"]),
                ]
            )
        if "height" in config:
            command.extend(
                [
                    "--height",
                    str(config["height"]),
                ]
            )
        if "margin" in config:
            command.extend(
                [
                    "--margin",
                    str(config["margin"]),
                ]
            )
        if "background_color" in config:
            command.extend(
                [
                    "--background-color",
                    config["background_color"],
                ]
            )
        if "folder" in config:
            command.extend(["--folder", config["folder"]])
        if "class_name" in config:
            command.extend(["--class", config["class_name"]])
        if "draw-cut-lines" in config:
            command.extend(["--draw-cut-lines", config["draw-cut-lines"]])
        
        try:
            subprocess.run(command, check=True)
            print(f"Configuration {i} completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error running configuration {i}: {e}")


if __name__ == "__main__":
    # Define different configurations for all decks
    base_urls = {
        #"edge_of_the_knive": "https://www.underworldsdb.com/shared.php?deck=0,EK1,EK2,EK3,EK4,EK5,EK6,EK7,EK8,EK9,EK10,EK11,EK12,EK13,EK14,EK15,EK16,EK17,EK18,EK19,EK20,EK21,EK22,EK23,EK24,EK25,EK26,EK27,EK28,EK29,EK30,EK31,EK32&format=rivals&deckname=Edge%20of%20the%20Knife%20Rivals%20Deck",
        #"reckless_fury": "https://www.underworldsdb.com/shared.php?deck=0,RF1,RF2,RF3,RF4,RF5,RF6,RF7,RF8,RF9,RF10,RF11,RF12,RF13,RF14,RF15,RF16,RF17,RF18,RF19,RF20,RF21,RF22,RF23,RF24,RF25,RF26,RF27,RF28,RF29,RF30,RF31,RF32&format=rivals&deckname=Reckless%20Fury%20Rivals%20Deck",
        "wrack_and_ruin": "https://www.underworldsdb.com/shared.php?deck=0,WR1,WR2,WR3,WR4,WR5,WR6,WR7,WR8,WR9,WR10,WR11,WR12,WR13,WR14,WR15,WR16,WR17,WR18,WR19,WR20,WR21,WR22,WR23,WR24,WR25,WR26,WR27,WR28,WR29,WR30,WR31,WR32&format=rivals&deckname=Wrack%20and%20Ruin%20Rivals%20Deck",
        #"blazing_assault": "https://www.underworldsdb.com/shared.php?deck=0,BL1,BL2,BL3,BL4,BL5,BL6,BL7,BL8,BL9,BL10,BL11,BL12,BL13,BL14,BL15,BL16,BL17,BL18,BL19,BL20,BL21,BL22,BL23,BL24,BL25,BL26,BL27,BL28,BL29,BL30,BL31,BL32&format=rivals&deckname=Blazing%20Assault%20Rivals%20Deck",
        #"emberstone_sentinels": "https://www.underworldsdb.com/shared.php?deck=0,ES1,ES2,ES3,ES4,ES5,ES6,ES7,ES8,ES9,ES10,ES11,ES12,ES13,ES14,ES15,ES16,ES17,ES18,ES19,ES20,ES21,ES22,ES23,ES24,ES25,ES26,ES27,ES28,ES29,ES30,ES31,ES32&format=rivals&deckname=Emberstone%20Sentinels%20Rivals%20Deck",
        #"pillage_and_plunder": "https://www.underworldsdb.com/shared.php?deck=0,PL1,PL2,PL3,PL4,PL5,PL6,PL7,PL8,PL9,PL10,PL11,PL12,PL13,PL14,PL15,PL16,PL17,PL18,PL19,PL20,PL21,PL22,PL23,PL24,PL25,PL26,PL27,PL28,PL29,PL30,PL31,PL32&format=rivals&deckname=Pillage%20and%20Plunder%20Rivals%20Deck",
        #"countdown_to_cataclysm": "https://www.underworldsdb.com/shared.php?deck=0,CC1,CC2,CC3,CC4,CC5,CC6,CC7,CC8,CC9,CC10,CC11,CC12,CC13,CC14,CC15,CC16,CC17,CC18,CC19,CC20,CC21,CC22,CC23,CC24,CC25,CC26,CC27,CC28,CC29,CC30,CC31,CC32&format=rivals&deckname=Countdown%20to%20Cataclysm%20Rivals%20Deck",
    }

    configs = []
    for deck_name, url in base_urls.items():
        configs.extend(
            [
                {
                    "url": url,
                    "output": f"rivals_decks/{deck_name}",
                    "format": "png",
                },
                {
                    "url": url,
                    "output": f"rivals_decks/mazo_{deck_name}.pdf",
                    "format": "pdf",
                    "folder": f"rivals_decks/{deck_name}",
                    "margin": 3,
                    "draw-cut-lines": "true",
                },
            ]
        )

    run_uw_images_to_pdf(configs)
