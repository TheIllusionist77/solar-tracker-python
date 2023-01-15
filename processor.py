import pygame, sys, pandas, time, datetime
import matplotlib.pyplot as plt
import tkinter as tk
from pygame.locals import *
pygame.init()

TINY_FONT = pygame.font.Font("freesansbold.ttf", 16)
SMALL_FONT = pygame.font.Font("freesansbold.ttf", 24)
FONT = pygame.font.Font("freesansbold.ttf", 32)
SCREEN = pygame.display.set_mode((1200, 480))
FPS = 30
CLOCK = pygame.time.Clock()

CALCULATE_RECT = pygame.Rect(45, 45, 240, 60)
EXCEL_RECT = pygame.Rect(45, 125, 240, 60)
GRAPH_RECT = pygame.Rect(45, 205, 240, 60)
DATA_RECT = pygame.Rect(45, 285, 240, 60)
SOLAR_RECT = pygame.Rect(45, 365, 240, 60)

mouse_x = 360
mouse_y = 240

lines_count_static = -3
cycle_number_static = 0
main_dict_static = {}
lines_list_static = []
breakdown_list_static = []
index_list_static = []
output_list_static = []

lines_count_tracking = -3
cycle_number_tracking = 0
main_dict_tracking = {}
lines_list_tracking = []
breakdown_list_tracking = []
index_list_tracking = []
output_list_tracking = []

shell_list = []
loaded_data = False

root = tk.Tk()
root.withdraw()

def output():
    global shell_list, SCREEN, TINY_FONT
    new_list = [i for i in shell_list]
    new_list.reverse()
    new_list = new_list[:11]
    count = len(new_list)
    for each in new_list:
        text = TINY_FONT.render(each, False, (255, 255, 255))
        SCREEN.blit(text, (320, 65 + (count * 26)))
        count -= 1
        
def load_data():
    global lines_count_static, cycle_number_static, lines_count_tracking, cycle_number_tracking, loaded_data
    
    SCREEN.fill((0, 0, 0))
    text = FONT.render("Please choose your save file!", False, (255, 255, 255))
    SCREEN.blit(text, (20, 20))
    pygame.display.update()
    
    SAVE_FILE = tk.filedialog.askopenfilename()
    
    shell_list.append("Reading from " + str(SAVE_FILE[-26:]) + ".")
    start_time = time.time()
    
    try:
        with open(SAVE_FILE, "r") as file:
            for line in file.readlines():
                if "Running" in line:
                    mode = "running"
                elif "Tracking" in line:
                    mode = "tracking"
                elif "Ended" not in line:
                    if mode == "running":
                        lines_count_static += 1
                        if lines_count_static >= 0:
                            lines_list_static.append(line)
                    if mode == "tracking":
                        lines_count_tracking += 1
                        if lines_count_tracking >= 0:
                            lines_list_tracking.append(line)
        shell_list.append("Loaded " + str(lines_count_static + lines_count_tracking) + " lines of data in " + str(round((time.time() - start_time) * 1000, 1)) + "ms.")
    except:
        return False

    start_time = time.time()
    for line in lines_list_static:
        cycle_number_static += 1
        new_list = []
        line = line.split(" - ", 100)
        for each in line:
            if not "Time" in each and not "Uptime" in each:
                each = int(''.join(filter(str.isdigit, each.split(": ", 100)[-1])))
            else:
                each = each.split(": ", 100)[-1]
            new_list.append(each)
        main_dict_static[cycle_number_static] = new_list
    for line in lines_list_tracking:
        cycle_number_tracking += 1
        new_list = []
        line = line.split(" - ", 100)
        for each in line:
            if not "Time" in each and not "Uptime" in each:
                each = int(''.join(filter(str.isdigit, each.split(": ", 100)[-1])))
            else:
                each = each.split(": ", 100)[-1]
            new_list.append(each)
        main_dict_tracking[cycle_number_tracking] = new_list
    shell_list.append("Processed " + str(cycle_number_static * 7 + cycle_number_tracking * 7) + " data points in " + str(round((time.time() - start_time) * 1000, 1)) + "ms.")

    start_time = time.time()
    for line in main_dict_static:
        temp_list = []
        index_list_static.append(line)
        for each in main_dict_static[line]:
            temp_list.append(each)
        output_list_static.append(temp_list)
    for line in main_dict_tracking:
        temp_list = []
        index_list_tracking.append(line)
        for each in main_dict_tracking[line]:
            temp_list.append(each)
        output_list_tracking.append(temp_list)
    shell_list.append("Formatted " + str(cycle_number_static * 7 + cycle_number_tracking * 7) + " data points in " + str(round((time.time() - start_time) * 1000, 1)) + "ms.")
    loaded_data = True

def excel_output(output_list_static, index_list_static, output_list_tracking, index_list_tracking):
    start_time = time.time()
    shell_list.append("Saving data to .xlsx files; this may take a few minutes.")
    output()
    pygame.display.update()
    df1 = pandas.DataFrame(output_list_static,
        index=index_list_static,
        columns=["Cycle", "Time", "Uptime", "Solar Wattage (mW)", "Solar Power Collected (mWh)", "Solar Efficiency (%)", "Brightness"])
    df2 = pandas.DataFrame(output_list_tracking,
        index=index_list_tracking,
        columns=["Cycle", "Time", "Uptime", "Solar Wattage (mW)", "Solar Power Collected (mWh)", "Solar Efficiency (%)", "Brightness"])
    current_date = datetime.datetime.now().strftime("%m-%d-%Y")
    current_time = datetime.datetime.now().strftime("%H_%M_%S")
    output_file_static = "static_sheet-" + str(current_date) + "-" + str(current_time) + ".xlsx"
    output_file_tracking = "tracking_sheet-" + str(current_date) + "-" + str(current_time) + ".xlsx"
    df1.to_excel(output_file_static)
    df2.to_excel(output_file_tracking)
    shell_list.append("Saved data to " + str(output_file_static) + " and " + str(output_file_tracking) + " in " + str(round((time.time() - start_time) * 1000, 1)) + "ms.")

def plot_output(output_list_static, lines_count_static, output_list_tracking, lines_count_tracking):
    start_time = time.time()
    cycle_static = []
    solar_power_static = []
    solar_efficiency_static = []
    brightness_static = []
    cycle_tracking = []
    solar_power_tracking = []
    solar_efficiency_tracking = []
    brightness_tracking = []
    figure, axis = plt.subplots(2, 3)
    
    for each in output_list_static:
        cycle_static.append(each[0])
        solar_power_static.append(each[4])
        solar_efficiency_static.append(each[5])
        brightness_static.append(each[6])
        
    for each in output_list_tracking:
        cycle_tracking.append(each[0])
        solar_power_tracking.append(each[4])
        solar_efficiency_tracking.append(each[5])
        brightness_tracking.append(each[6])
      
    axis[0, 0].plot(cycle_static, solar_power_static)
    axis[0, 0].set_xlabel("Cycle (Static)")
    axis[0, 0].set_ylabel("Power Collected (mWh)")
    
    axis[0, 1].plot(cycle_static, solar_efficiency_static)
    axis[0, 1].set_xlabel("Cycle (Static)")
    axis[0, 1].set_ylabel("Solar Efficiency (%)")
    
    axis[0, 2].plot(cycle_static, brightness_static)
    axis[0, 2].set_xlabel("Cycle (Static)")
    axis[0, 2].set_ylabel("Brightness (100nF/10MΩ)")
    
    axis[1, 0].plot(cycle_tracking, solar_power_tracking)
    axis[1, 0].set_xlabel("Cycle (Tracking)")
    axis[1, 0].set_ylabel("Power Collected (mWh)")
    
    axis[1, 1].plot(cycle_tracking, solar_efficiency_tracking)
    axis[1, 1].set_xlabel("Cycle (Tracking)")
    axis[1, 1].set_ylabel("Solar Efficiency (%)")
    
    axis[1, 2].plot(cycle_tracking, brightness_tracking)
    axis[1, 2].set_xlabel("Cycle (Tracking)")
    axis[1, 2].set_ylabel("Brightness (100nF/10MΩ)")
    
    SCREEN.fill((0, 0, 0))
    text = SMALL_FONT.render("You need to close the graph window to resume interaction with this application.", False, (255, 255, 255))
    text2 = SMALL_FONT.render("Use the buttons in the bottom-left corner to zoom, save and more.", False, (255, 255, 255))
    SCREEN.blit(text, (20, 20))
    SCREEN.blit(text2, (20, 48))
    pygame.display.update()
    shell_list.append("Graphs rendered in " + str(round((time.time() - start_time) * 1000, 1)) + "ms.")
    pygame.display.update()
    plt.show()
    
def raw_output(output_list_static, output_list_tracking):
    average_wattage_static = 0
    for each in output_list_static:
        average_wattage_static += each[3]
    average_wattage_static /= lines_count_static
    final_power_static = output_list_static[lines_count_static - 1][4]
    efficiency_static = output_list_static[lines_count_static - 1][5]
    average_brightness_static = 0
    for each in output_list_static:
        average_brightness_static += each[6]
    average_brightness_static /= lines_count_static
        
    cycles = output_list_tracking[lines_count_tracking - 1][0]
    duration = output_list_tracking[lines_count_tracking - 1][2]
    average_wattage_tracking = 0
    for each in output_list_tracking:
        average_wattage_tracking += each[3]
    average_wattage_tracking /= lines_count_tracking
    final_power_tracking = output_list_tracking[lines_count_tracking - 1][4]
    efficiency_tracking = output_list_tracking[lines_count_tracking - 1][5]
    average_brightness_tracking = 0
    for each in output_list_tracking:
        average_brightness_tracking += each[6]
    average_brightness_tracking /= lines_count_tracking
        
    shell_list.append("Cycles Ran: " + str(int(cycles)))
    shell_list.append("Total Uptime: " + str(duration))
    shell_list.append("Average Power Input (Static): " + str(round(average_wattage_static)) + "mW")
    shell_list.append("Total Power Collected (Static): " + str(final_power_static) + "mWh")
    shell_list.append("Solar Efficiency (Static): " + str(efficiency_static) + "%")
    shell_list.append("Brightness (Static): " + str(round(average_brightness_static)))
    shell_list.append("Average Power Input (Tracking): " + str(round(average_wattage_tracking)) + "mW")
    shell_list.append("Total Power Collected (Tracking): " + str(final_power_tracking) + "mWh")
    shell_list.append("Solar Efficiency (Tracking): " + str(efficiency_tracking) + "%")
    shell_list.append("Brightness (Tracking): " + str(round(average_brightness_tracking)))
    shell_list.append("Tracking Gain: " + str(round((efficiency_tracking / efficiency_static) * 100)) + "%")

def solar_output(output_list_static, output_list_tracking):
    efficiency_static = output_list_static[lines_count_static - 1][5]
    efficiency_tracking = output_list_tracking[lines_count_static - 1][5]
    SCREEN.fill((0, 0, 0))
    text = FONT.render("Please look in the terminal; we need some information!", False, (255, 255, 255))
    SCREEN.blit(text, (20, 20))
    pygame.display.update()
    shell_list.append("We need to collect some information before we give you a personalized solar report.")
    power_cost = input("Enter the cost of your electricity over the past month (the U.S. average is $122) [$]: ")
    power_amount = input("Enter the amount of electricity your household used over the past month (the U.S. average is 886kWh) [kWh]: ")
    cost_per_watt = input("Enter the cost per watt of the solar panels you are looking to buy, including installation fees (the U.S. average is $2.77) [$]: ")
    print("Your job in the terminal has finished! You can now go back to the application.")
    watts_needed_static = (float(power_amount) * 1000 / 730) / (efficiency_static / 100)
    watts_needed_tracking = (float(power_amount) * 1000 / 730) / (efficiency_tracking / 100)
    shell_list.append("You would need about " + str(round(watts_needed_static)) + " watts of static solar panels to cover the needs of your household.")
    shell_list.append("You would need about " + str(round(watts_needed_tracking)) + " watts of tracking solar panels to cover the needs of your household.")
    total_cost_static = float(watts_needed_static) * float(cost_per_watt)
    total_cost_tracking = float(watts_needed_tracking) * float(cost_per_watt)
    shell_list.append("To buy that many static solar panels at the price per panel provided, it would cost you $" + str(round(total_cost_static, 2)) + ".")
    shell_list.append("To buy that many tracking solar panels at the price per panel provided, it would cost you $" + str(round(total_cost_tracking, 2)) + ".")
    break_even = round(total_cost_static * 100 / total_cost_tracking)
    shell_list.append("If you break even in cost, you could afford to pay " + str(break_even - 100) + "% more per panel for solar tracking ones.")
    repay_time_static = total_cost_static / (float(power_cost) * 12)
    repay_time_tracking = total_cost_tracking / (float(power_cost) * 12)
    repay_time_even = repay_time_tracking * break_even / 100
    shell_list.append("The static solar panels will pay themselves off after " + str(round(repay_time_static, 1)) + " years.")
    shell_list.append("The tracking solar panels will pay themselves off after " + str(round(repay_time_tracking, 1)) + " years.")
    shell_list.append("The tracking solar panels, at a " + str(break_even) + "% extra cost would pay themselves off after " + str(round(repay_time_even, 1)) + " years.")

while True:
    SCREEN.fill((0, 0, 0))
    left_click = False
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == MOUSEMOTION:
            mouse_x, mouse_y = event.pos
        if event.type == MOUSEBUTTONDOWN:
            left_click = True
    try:     
        if CALCULATE_RECT.collidepoint(mouse_x, mouse_y) == True:
            pygame.draw.rect(SCREEN, (205, 205, 205), CALCULATE_RECT)
            if left_click == True:
                if loaded_data == True:
                    lines_count_static = -3
                    cycle_number_static = 0
                    main_dict_static = {}
                    lines_list_static = []
                    breakdown_list_static = []
                    index_list_static = []
                    output_list_static = []
                    lines_count_tracking = -3
                    cycle_number_tracking = 0
                    main_dict_tracking = {}
                    lines_list_tracking = []
                    breakdown_list_tracking = []
                    index_list_tracking = []
                    output_list_tracking = []
                load_data()
        else:
            pygame.draw.rect(SCREEN, (255, 255, 255), CALCULATE_RECT)
            
        if EXCEL_RECT.collidepoint(mouse_x, mouse_y) == True:
            pygame.draw.rect(SCREEN, (205, 205, 205), EXCEL_RECT)
            if left_click == True:
                if loaded_data:
                    excel_output(output_list_static, index_list_static, output_list_tracking, index_list_tracking)
                else:
                    shell_list.append("Load your data first!")
        else:
            pygame.draw.rect(SCREEN, (255, 255, 255), EXCEL_RECT)
            
        if GRAPH_RECT.collidepoint(mouse_x, mouse_y) == True:
            pygame.draw.rect(SCREEN, (205, 205, 205), GRAPH_RECT)
            if left_click == True:
                if loaded_data:
                    plot_output(output_list_static, lines_count_static, output_list_tracking, index_list_tracking)
                else:
                    shell_list.append("Load your data first!")
        else:
            pygame.draw.rect(SCREEN, (255, 255, 255), GRAPH_RECT)
    
        if DATA_RECT.collidepoint(mouse_x, mouse_y) == True:
            pygame.draw.rect(SCREEN, (205, 205, 205), DATA_RECT)
            if left_click == True:
                if loaded_data:
                    raw_output(output_list_static, output_list_tracking)
                else:
                    shell_list.append("Load your data first!")
        else:
            pygame.draw.rect(SCREEN, (255, 255, 255), DATA_RECT)
            
        if SOLAR_RECT.collidepoint(mouse_x, mouse_y) == True:
            pygame.draw.rect(SCREEN, (205, 205, 205), SOLAR_RECT)
            if left_click == True:
                if loaded_data:
                    solar_output(output_list_static, output_list_tracking)
                else:
                    shell_list.append("Load your data first!")
        else:
            pygame.draw.rect(SCREEN, (255, 255, 255), SOLAR_RECT)
    except ZeroDivisionError:
        shell_list.append("Something went wrong. If you continue to get this error, your data file may be faulty.")
    
    if not loaded_data:
        text = FONT.render("Process Data", False, (0, 0, 0))
        SCREEN.blit(text, (65, 60))
    else:
        text = FONT.render("Reload Data", False, (0, 0, 0))
        SCREEN.blit(text, (67.5, 60))
    
    text = FONT.render("Save as .xlsx", False, (0, 0, 0))
    SCREEN.blit(text, (62.5, 140))
    
    text = FONT.render("Graph results", False, (0, 0, 0))
    SCREEN.blit(text, (60, 220))
    
    text = FONT.render("View raw data", False, (0, 0, 0))
    SCREEN.blit(text, (57.5, 300))
    
    text = FONT.render("Get estimate", False, (0, 0, 0))
    SCREEN.blit(text, (60, 380))
    
    text = SMALL_FONT.render("Output:", False, (255, 255, 255))
    SCREEN.blit(text, (320, 60))
    
    output()
    
    pygame.display.update()
    CLOCK.tick(FPS)