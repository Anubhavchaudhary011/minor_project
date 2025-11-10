import tkinter as tk
from tkinter import ttk
from utils.reddit_fetcher import fetch_reddit_posts


class RedditWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Reddit Fetcher – Minor Project")
        self.root.geometry("650x500")

        self.title_label = tk.Label(self.root, text="Reddit Post Fetcher", font=("Arial", 16, "bold"))
        self.title_label.pack(pady=15)

        # Subreddit input box
        self.subreddit_label = tk.Label(self.root, text="Enter Subreddit:", font=("Arial", 12))
        self.subreddit_label.pack()

        self.subreddit_entry = tk.Entry(self.root, width=40, font=("Arial", 12))
        self.subreddit_entry.insert(0, "python")
        self.subreddit_entry.pack(pady=8)

        # Button to fetch posts
        self.fetch_button = tk.Button(
            self.root,
            text="Fetch Reddit Posts",
            font=("Arial", 12),
            command=self.fetch_posts
        )
        self.fetch_button.pack(pady=10)

        # Listbox to display posts
        self.posts_list = tk.Listbox(self.root, width=80, height=20, font=("Arial", 10))
        self.posts_list.pack(pady=10)

        self.root.mainloop()

    def fetch_posts(self):
        subreddit = self.subreddit_entry.get().strip()
        self.posts_list.delete(0, tk.END)

        posts = fetch_reddit_posts(subreddit)

        for p in posts:
            self.posts_list.insert(tk.END, p)


if __name__ == "__main__":
    RedditWindow()
