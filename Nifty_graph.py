import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("nifty.csv")
data["Date"] = pd.to_datetime(data["Date"], dayfirst=True)
data["Open"] = data["Open"].str.replace(",", "").astype(float)
data = data.sort_values("Date")

plt.figure(figsize=(12, 6))
plt.plot(data["Date"], data["Open"])

plt.title("NIFTY Open Price")
plt.xlabel("Date")
plt.ylabel("Open Price")

plt.grid(True)
plt.tight_layout()
plt.show()