# 🐶 Government Payments Scraper  

This is a **multi-threaded web scraper** that extracts **payment data** from the [DOGE Government Payments website](https://doge.gov/payments) using **Selenium** and **Python**.  

## **📌 Features**
✅ **Automates filtering by request date** (clicks each date to filter the table).  
✅ **Scrapes paginated table data** until the last page.  
✅ **Extracts all available dates first** before scraping.  
✅ **Uses multi-threading** (`ThreadPoolExecutor`) for faster data extraction.  
✅ **Exports data to CSV** (`filtered_payments.csv`) with a "REQUEST DATE" column.  

---

## **🔧 Installation**
### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/your-username/doge-payments-scraper.git
cd doge-payments-scraper
