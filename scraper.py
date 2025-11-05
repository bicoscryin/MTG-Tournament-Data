# Import libraries
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import pandas as pd
from pathlib import Path

# Defines a df for all paticipants in this tournament and their basic stats
list_of_table_columns = ["Rank","Player Name", "Deck Name", "Match Record", "Game Record", "Points", "OMW%", "TGW%", "OGW%", "Player Name", 'Player URL', "Decklist URL"]
PARTICIPANT_DF = pd.DataFrame(columns=list_of_table_columns)


#Browser initialization
browser = webdriver.Chrome()
#Workaround for "Help" button stopping the script from clicking on the "Next Page" button while grabbing Tournamanet results
browser.set_window_size(2000,800)
wait = WebDriverWait(browser, timeout=10)

# Functions
def set_tournament_participants(url: str) -> pd.DataFrame:
    """Will get all participants for a tournament and save it in participant_loop_df"""
    # Prevents this function from running if the first player in the table has not loaded
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#tournament-standings-table > tbody > tr:nth-child(1) > td.Player-column > div > div > a")))
    participant_loop_df = pd.DataFrame(columns=["Rank","Player Name", "Deck Name", "Match Record", "Game Record", "Points", "OMW%", "TGW%", "OGW%", "Player Profile Name", 'Player Profile URL', "Decklist URL"])
    # Iterates through all the participants and stores a cleaned version of their data in participant_loop_df
    for i in range(participant_count()):
        table_row_list = []
        i += 1
        if i % 25 == 0:
            for ele in browser.find_element(By.CSS_SELECTOR, f"#tournament-standings-table > tbody > tr:nth-child({25})").find_elements(By.TAG_NAME, "td"):
                table_row_list.append(ele.get_property("innerHTML"))
            next_table_page()
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#tournament-standings-table > tbody > tr:nth-child(1) > td.Player-column > div > div > a")))
        else:
            for ele in browser.find_element(By.CSS_SELECTOR, f"#tournament-standings-table > tbody > tr:nth-child({i % 25})").find_elements(By.TAG_NAME, "td"):
                table_row_list.append(ele.get_property("innerHTML"))
        participant_loop_df.loc[clean_results_table(table_row_list, url)[0]] = clean_results_table(table_row_list, url)
    #Set the Column Match Total from Match Record
    for i in range(len(participant_loop_df["Match Record"])):
        i += 1
        participant_loop_df.loc[[i],"Match Total"] = sum(participant_loop_df["Match Record"][i])
    return participant_loop_df
def set_match_results_and_decklists(participants: pd.DataFrame, function_directory: str) -> pd.DataFrame:
    """Will retrieve all decklists and match results from a tournament using the PARTICIPANT_DF for basic information"""
    #must set a loop dataframe so it can be exported (can't set a variable inside a function)
    decklists_funtion_df = pd.DataFrame(columns=["Card Quantity", "Card Name","Profile Name","Deck Name"])
    rounds_function_df = pd.DataFrame(columns=["Round","Result", "Player Profile", "Opponent Profile", "Record"])
    for i, url in enumerate(participants["Decklist URL"]):
        #Adjusting index to match index of dataframe
        i += 1
        #opens the page and waits till it has loaded
        browser.get(url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "a")))
        try:
        #Tests if Round Results have been recorded yet
            check_file_location(f"{function_directory}all_round_results.csv")
        except:
            #Will record round results for each player in participants
            for idx in range(participants["Match Total"][i].astype(int)):
                #Iterates through all rounds this player has played
                table_row_list = []
                idx += 1
                try:
                    #Makes sure that this element is present on that page
                    for ele in browser.find_element(By.CSS_SELECTOR, f"#decklist-tournament-path-container > div > table > tbody > tr:nth-child({idx})").find_elements(By.TAG_NAME, "td"):
                        #pulls all the data from a single round
                        table_row_list.append(ele.get_property("innerHTML"))
                except:
                    print(f"Cannot grab round data for {url}")
                    break
                else:
                    #Inserts one round into a row of the match results df
                    rounds_function_df.loc[len(rounds_function_df)] = clean_round_data(table_row_list, participants.loc[i,"Player Profile Name"], participants)
        try:
        #Tests if Decklists have been recorded
            check_file_location(f"{function_directory}all_decklists.csv")
        except:
        #Will record all Decklists for players in participants
            try:
                #Makes sure that this element is present on that page
                decklist_df = pd.DataFrame(set_decklist_as_tuple(),columns=["Card Quantity", "Card Name"])
            except:
                print(f"Cannot grab decklist data for {url}")
                pass
            else:
                decklist_df["Profile Name"] = participants.loc[i,"Player Profile Name"]
                decklist_df["Deck Name"] = participants.loc[i,"Deck Name"]
                #Add Thos Player's Decklist to the Complete decklist table
                decklists_funtion_df = pd.concat([decklists_funtion_df,decklist_df])
                #ALL_DECKLISTS = pd.concat([ALL_DECKLISTS, decklist_df]) # can't set a variable inside a function
    return rounds_function_df, decklists_funtion_df
def current_page() -> tuple:
    """returns the standing for the first and the last participant on the page"""
    first_num: int = int(browser.find_element(By.CSS_SELECTOR, "#tournament-standings-table_info").get_property("innerHTML").split(" ")[1])
    sec_num: int = int(browser.find_element(By.CSS_SELECTOR, "#tournament-standings-table_info").get_property("innerHTML").split(" ")[3])
    return (first_num, sec_num)
def participant_count() -> int:
    """returns the total number of participants in the tournament"""
    return int(browser.find_element(By.CSS_SELECTOR, "#tournament-standings-table_info").get_property("innerHTML").split(" ")[5].replace(",",""))
def next_table_page() -> None:
    """clicks the next page for the table of participants"""
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#tournament-standings-table_next")))
    browser.find_element(By.CSS_SELECTOR, "#tournament-standings-table_next").click()
def previous_table_page() -> None:
    """clicks the previous page for the table of participants"""
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#tournament-standings-table_next")))
    browser.find_element(By.CSS_SELECTOR, "#tournament-standings-table_previous").click()
def url_column(multi_line:str, url: str) -> str:
    """Input is either Players/Teams or Decklist column in the results table. It will return the url of the input as well as the player/decklist name and profile name."""
    #split data into lines and take the 3rd item (Main body of data) then split it by ">" (separates name and url)
    clean_data = multi_line.split("\n")[2].split(">")
    try:
        #split the second item in clean data by "<" to isolate the name and replace "," and "."
        clean_name = clean_data[1].split("<")[0].replace(",","").replace(".","").strip()
    except:
        #If there is no data, return none and the url of the tournament
        clean_name = 'None'
        profile_name = 'None'
        web_address = url
    else:
        #join list parts to create a single string for the name
        clean_name = "".join(clean_name)
        #split the first item in clean data by " and take the second to last item to get ending url
        clean_url = clean_data[0].split("\"")[-2]
        #add base web to ending url
        web_address = "https://melee.gg" + clean_url
        profile_name = clean_url.split("/")[-1].strip()
    return clean_name , web_address , profile_name
def percentage_column(single_line:str) -> float:
    """Input is the OMW/TGW/OGW column in the results table. It return a percentage(whole number) float."""
    clean_data = single_line.split("\"")[2].split("%")[0].split(">")[1]
    return float(clean_data)
def record_column(single_string: str) -> list:
    """Converts a Match/Game record into an integer list of each element(first is wins, second is losses, third is draws)"""
    clean_data = [int(i) for i in (single_string.split("-"))]
    return clean_data
def string_to_integer(single_string: str) -> int:
    """Transforms a string into a integer"""
    return int(single_string)
def clean_results_table(table_list: list, url: str) -> dict:
    """Input a list of one row from the results table. It converts Rank/Points to integers.
    It converts Players/Decklist to urls. It converts Match/Game Records to a list.
    It converts win percentages to a float"""
    loop_list = table_list.copy()
    for i in range(len(table_list)):
        if i == 0 or i == 5:
            #Rank and Points
            loop_list[i] = string_to_integer(table_list[i])
        elif i == 1:
            #User Profile URL and Player Name
            loop_list[i] = url_column(table_list[i], url)[0]
            loop_list.append(url_column(table_list[i], url)[2])
            loop_list.append(url_column(table_list[i], url)[1])
        elif i == 2:
            #Decklist URL and Deck Name
            loop_list[i] = url_column(table_list[i], url)[0]
            loop_list.append(url_column(table_list[i], url)[1])
        elif 3 == i or i == 4:
            #Record
            loop_list[i] = record_column(table_list[i])
        elif i > 5:
            #Win Percentages
            loop_list[i] = percentage_column(table_list[i])
    return loop_list
def clean_round_data(table_list: list, player: str, participant: pd.DataFrame) -> list:
    """Cleans up round data and returns usable strings and integers"""
    #set variables for winner,player, and opponent
    loop_list = table_list.copy()
    #Set round and notes(append needed since we are adding notes)
    loop_list[0] = string_to_integer(table_list[0])
    loop_list.append(result_column(table_list[3], participant)[1])
    #Places the winner(or draw) in results
    loop_list[1] = result_column(table_list[3], participant)[0]
    #Opponent
    loop_list[3] = string_column(table_list[1], participant)
    #Player
    loop_list[2] = string_column(player, participant)
    return loop_list
def clean_bye_round(result_list:list, participant: pd.DataFrame) -> list:
    """Returns a usable list of what data will be used for a bye"""
    loop_list = result_list.copy()
    for ele in loop_list:
        try:
            profile_name += (f' {ele.replace(",","").replace(".","").strip()}')
        except:
            profile_name = ele
        if not participant[participant['Player Name'] == profile_name].empty:
            break
    return profile_name.strip() , loop_list[-1].capitalize().strip()
def reverse_name_order(inner_html:str) -> str:
    """Flip the ordering of a name. ie: Smith, John to John Smith"""
    reversed_name = inner_html.split(",")
    loop_list = []
    for i in range(len(reversed_name)):
        if i == 0:
            loop_list.append(reversed_name[-1].strip())
        if i > 0:
            loop_list.append(reversed_name[i-1].strip())
    reversed_name = " ".join(loop_list)
    return reversed_name
def string_column(one_line: str, participant: pd.DataFrame) -> str:
    """Converts Opponent and Decklist to usable strings(from Decklist). 
    It also removes "," and "." """
    if ">" not in one_line:
        return one_line
    clean_line = one_line.split(">")[1].split('<')[0].replace(",","").replace(".","").strip()
    try:
        clean_line = participant[participant['Player Name'] == clean_line]['Player Profile Name'].values[0]
    except:
        pass
    return clean_line
def result_column(result_str:str, participant: pd.DataFrame) -> list:
    """Input the result string form tournament path and recieve winner and match record."""
    if ' bye' in result_str.lower(): #check if it was a bye
        loop_list = clean_bye_round(result_str.split(" "), participant)
        notes = loop_list[1]
        winner = loop_list[0]
        return winner, notes
    if '-' not in result_str: #Test if there is a match record (ie 2-1-0)
        notes = result_str.strip()
        winner = ''
        return winner, notes
    #splits string on spaces
    result_str = result_str.split(" ")
    #remove the last two elements to preserve any abnormal names
    notes = []
    for i in range(2):
        notes.append(result_str.pop())
    #Checks if the match was a draw
    if "Draw" in notes:
        winner = "Draw"
        #Return Recrord
        notes = notes[1]
    else:
        #Return record
        notes = notes[0]
        #assigns the rest of the string (Name) to winner
        winner = " ".join(result_str).replace(",","").replace(".","").strip()
        #Get the player profile name from the player name
        winner = participant[participant['Player Name'] == winner]['Player Profile Name'].values[0]
    return winner, notes
def set_decklist_as_tuple() -> list:
    """Grabs the decklist from the current page the browser is at.
      It returns it as a list of tuples"""
    #this function meant to be used inside a loop going through a list of urls
    card_tuple = []
    card_num_list = []
    card_name_list = []
    for ele in browser.find_element(By.CSS_SELECTOR, f"body > div.content.page-with-container > div > div.decklist-container").find_elements(By.TAG_NAME, "a"):
        card_name_list.append(ele.get_property("innerHTML"))
    for ele in browser.find_element(By.CSS_SELECTOR, f"body > div.content.page-with-container > div > div.decklist-container").find_elements(By.TAG_NAME, "span"):
        card_num_list.append(int(ele.get_property("innerHTML")))
    if card_num_list or card_num_list:
        for ele in list(zip(*[card_num_list,card_name_list])):
            card_tuple.append(ele)
    return card_tuple
def clean_decklist_name(play_name: str, deck_name: str) -> str:
    """Outputs a decklist name that is free from bad puctuation"""
    play_name = play_name.replace(" ", "_").replace("\"", "").replace("\'","").replace("\\","").replace(".","").strip()
    deck_name = deck_name.replace(" ", "_").replace("\"", "").replace("\'","").replace("\\","").replace(".","").strip()
    return f"{play_name}_{deck_name}.csv"
def check_file_location(file_path: str):
    """Checks if a file exists at the file path you give it"""
    return Path(file_path).resolve(strict=True)
def remove_duplicate_matches(full_match_results):
    """Takes the full list of all rounds and removes any duplicates"""
    unique_winner = full_match_results[full_match_results["Player Profile"] == full_match_results["Result"]].copy()
    match_results_draw = full_match_results[full_match_results["Result"] == "Draw"].copy()
    unique_draw = pd.DataFrame(columns=match_results_draw.columns)
    for ele in match_results_draw.values:
        if unique_draw.empty:
            unique_draw.loc[len(unique_draw)] = ele
        elif ele[2] not in unique_draw[unique_draw["Round"] == ele[0]]['Opponent Profile'].values and ele[2] not in unique_draw[unique_draw["Round"] == ele[0]]['Player Profile'].values:
            unique_draw.loc[len(unique_draw)] = ele
    unique_full_results = pd.concat([unique_draw,unique_winner])
    return unique_full_results