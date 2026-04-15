from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import os

# ================= CẤU HÌNH =================
BASE_URL = "https://www.futoshiki.com/"

# Tên thư mục chứa các file txt (Code sẽ tự tạo nếu chưa có)
OUTPUT_DIR = "input"

# Kích thước bảng (từ 4x4 đến 9x9)
sizes = [4, 5, 6, 7, 8, 9]

# Các độ khó
difficulties = ["trivial", "easy", "tricky", "extreme"]

# Số lượng đề test muốn cào cho MỖI độ khó (Ví dụ: 3)
tests_per_config = 3
# ============================================

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


def parse_board(driver, n):
    """Quét DOM để lấy dữ liệu số và bất đẳng thức"""
    table = driver.find_element(By.ID, "boardTable")
    trs = table.find_elements(By.XPATH, "./tbody/tr")

    grid, horiz, vert = [], [], []

    # 1. Quét lưới số (Grid) và Bất đẳng thức ngang (Horizontal)
    for r in range(n):
        row_cells = trs[2 * r].find_elements(By.TAG_NAME, "td")
        current_grid_row, current_horiz_row = [], []

        # Quét số
        for c in range(n):
            val = row_cells[2 * c].text.strip()
            current_grid_row.append(val if val else "0")

        # Quét dấu ngang (<, >)
        for c in range(n - 1):
            h_cell = row_cells[2 * c + 1]
            imgs = h_cell.find_elements(By.TAG_NAME, "img")
            if imgs:
                src = imgs[0].get_attribute("src")
                if "l0.gif" in src:
                    current_horiz_row.append("1")  # <
                elif "r0.gif" in src:
                    current_horiz_row.append("-1")  # >
                else:
                    current_horiz_row.append("0")
            else:
                current_horiz_row.append("0")

        grid.append(current_grid_row)
        horiz.append(current_horiz_row)

    # 2. Quét Bất đẳng thức dọc (Vertical)
    for r in range(n - 1):
        row_cells = trs[2 * r + 1].find_elements(By.TAG_NAME, "td")
        current_vert_row = []

        # Quét dấu dọc (^, v)
        for c in range(n):
            v_cell = row_cells[2 * c]
            imgs = v_cell.find_elements(By.TAG_NAME, "img")
            if imgs:
                src = imgs[0].get_attribute("src")
                if "u0.gif" in src:
                    current_vert_row.append("1")  # ^ (top < bottom)
                elif "d0.gif" in src:
                    current_vert_row.append("-1")  # v (top > bottom)
                else:
                    current_vert_row.append("0")
            else:
                current_vert_row.append("0")

        vert.append(current_vert_row)

    return grid, horiz, vert


def write_to_txt(filename, n, grid, horiz, vert):
    """Lưu dữ liệu ra file text theo định dạng yêu cầu"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"{n}\n")
        f.write("# Grid: N lines of N values separated by commas.\n")
        f.write("# 0 = empty cell; 1..N = pre-filled digit.\n")
        for row in grid:
            f.write(", ".join(row) + "\n")

        f.write("# Horizontal constraints: one line per row, N-1 values.\n")
        f.write("# 0 = no constraint, 1 = \"<\" (left < right), -1 = \">\" (left > right)\n")
        for row in horiz:
            f.write(", ".join(row) + "\n")

        f.write("# Vertical constraints: one line per row (N-1 lines), N values.\n")
        f.write("# 0 = no constraint, 1 = \"<\" (top < bottom), -1 = \">\" (top > bottom)\n")
        for row in vert:
            f.write(", ".join(row) + "\n")


# ================= MAIN =================
driver = webdriver.Chrome()
driver.get(BASE_URL)
time.sleep(2)

for size in sizes:
    # Mở dropdown Size và chọn
    size_dropdown = Select(driver.find_element(By.ID, "ssize"))
    size_dropdown.select_by_visible_text(str(size))
    time.sleep(1)

    for diff in difficulties:
        for test_num in range(1, tests_per_config + 1):

            # --- TÊN FILE ĐƯỢC TẠO Ở ĐÂY ĐÚNG YÊU CẦU CỦA BẠN ---
            filename = f"size{size}_{diff}_{test_num}.txt"
            # ---------------------------------------------------

            print(f"Đang cào: {filename}...")

            # Chọn Độ khó
            diff_dropdown = Select(driver.find_element(By.ID, "sdif"))
            diff_dropdown.select_by_visible_text(diff)

            # Gọi hàm JS của trang web để sinh map mới
            diff_value = diff_dropdown.first_selected_option.get_attribute("value")
            driver.execute_script(f"fetchGame({diff_value});")
            time.sleep(1.5)  # Đợi trang load bảng mới

            try:
                grid, horiz, vert = parse_board(driver, size)
                write_to_txt(filename, size, grid, horiz, vert)
            except Exception as e:
                print(f"Lỗi ở map {filename}: {e}")

print(f"\n✅ HOÀN THÀNH! Tất cả file đã được lưu vào thư mục: {os.path.abspath(OUTPUT_DIR)}")
driver.quit()