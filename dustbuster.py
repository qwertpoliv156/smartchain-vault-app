"""
DustBuster: Обнаружение "пылевых атак" (dust attacks) на Bitcoin-кошельки.
"""

import requests
import argparse

DUST_THRESHOLD = 0.00001  # BTC, порог для пыли (~1000 сатоши)

def fetch_transactions(address):
    url = f"https://api.blockchair.com/bitcoin/dashboards/address/{address}"
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception("Ошибка получения данных по адресу.")
    return r.json()["data"][address]["transactions"]

def fetch_transaction_details(txid):
    url = f"https://api.blockchair.com/bitcoin/raw/transaction/{txid}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()["data"][txid]["decoded_raw_transaction"]

def satoshi_to_btc(sats):
    return sats / 100000000

def analyze_dust(address):
    print(f"🧹 Анализ пылевых атак на адрес: {address}")
    txs = fetch_transactions(address)
    dust_txs = []

    for txid in txs[:50]:  # Проверяем последние 50 транзакций
        tx = fetch_transaction_details(txid)
        if not tx:
            continue

        outputs = tx.get("vout", [])
        for o in outputs:
            value = float(o.get("value", 0))
            if value < DUST_THRESHOLD:
                addresses = o.get("script_pub_key", {}).get("addresses", [])
                if address in addresses:
                    dust_txs.append((txid, value))

    print(f"🔎 Найдено подозрительных пылевых транзакций: {len(dust_txs)}")

    if dust_txs:
        print("⚠️ Подробности:")
        for txid, value in dust_txs:
            print(f"  - TXID: {txid}, сумма: {value} BTC")
    else:
        print("✅ Пылевых атак не обнаружено.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DustBuster — выявление dust-атак на Bitcoin-кошельки.")
    parser.add_argument("address", help="Bitcoin-адрес для анализа")
    args = parser.parse_args()
    analyze_dust(args.address)
