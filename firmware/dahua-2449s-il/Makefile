
# Makefile для сборки Camera Agent для dahua-2449s-il

CC = gcc
CFLAGS = -Wall -Wextra -O2
PYTHON = python3

# Платформа
PLATFORM = linux_arm
ARCH = armv7

# Директории
SRC_DIR = agent
BUILD_DIR = build
DIST_DIR = dist

.PHONY: all clean build package install

all: build package

build:
	@echo "[BUILD] Сборка Camera Agent..."
	mkdir -p $(BUILD_DIR)
	$(PYTHON) -m py_compile $(SRC_DIR)/**/*.py
	cp -r $(SRC_DIR) $(BUILD_DIR)/
	cp config.json $(BUILD_DIR)/

package:
	@echo "[PACKAGE] Создание пакета..."
	mkdir -p $(DIST_DIR)
	tar -czf $(DIST_DIR)/dahua-2449s-il_firmware.tar.gz \
		$(BUILD_DIR)/* \
		install.sh \
		uninstall.sh

clean:
	@echo "[CLEAN] Очистка..."
	rm -rf $(BUILD_DIR) $(DIST_DIR)

install: build package
	@echo "[INSTALL] Установка..."
	./install.sh

# Цель для кросс-компиляции (если нужно)
cross-compile:
	@echo "[CROSS-COMPILE] Кросс-компиляция для $(PLATFORM)..."
	# TODO: Добавить команды кросс-компиляции
