#!/usr/bin/env python3
import argparse
import json
import os
import sys
from typing import List, Dict, Any

BOOKS_FILE = os.environ.get("BOOKS_FILE", "books.json")

def load_books() -> List[Dict[str, Any]]:
    if not os.path.exists(BOOKS_FILE):
        return []
    try:
        with open(BOOKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: {BOOKS_FILE} is not valid JSON.", file=sys.stderr)
        sys.exit(1)

def save_books(books: List[Dict[str, Any]]) -> None:
    with open(BOOKS_FILE, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)
        f.write("\n")

def ensure_unique_id(books: List[Dict[str, Any]], book_id: int) -> None:
    if any(b["id"] == book_id for b in books):
        print(f"Error: A book with id {book_id} already exists.", file=sys.stderr)
        sys.exit(1)

def get_book_index(books: List[Dict[str, Any]], book_id: int) -> int:
    for i, b in enumerate(books):
        if b["id"] == book_id:
            return i
    print(f"Error: Book with id {book_id} not found.", file=sys.stderr)
    sys.exit(1)

def cmd_init(_: argparse.Namespace) -> None:
    if os.path.exists(BOOKS_FILE):
        print(f"{BOOKS_FILE} already exists.")
        return
    save_books([])
    print(f"Created empty {BOOKS_FILE}")

def cmd_list(args: argparse.Namespace) -> None:
    books = load_books()
    if args.pretty:
        print(json.dumps(books, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(books, ensure_ascii=False))

def cmd_get(args: argparse.Namespace) -> None:
    books = load_books()
    idx = get_book_index(books, args.id)
    print(json.dumps(books[idx], indent=2, ensure_ascii=False))

def cmd_add(args: argparse.Namespace) -> None:
    books = load_books()
    ensure_unique_id(books, args.id)
    book = {
        "id": args.id,
        "title": args.title,
        "author": args.author,
        "year": args.year,
        "genres": args.genres or [],
        "in_stock": args.in_stock
    }
    books.append(book)
    save_books(books)
    print(f"Added book id {args.id}")

def cmd_update(args: argparse.Namespace) -> None:
    books = load_books()
    idx = get_book_index(books, args.id)
    book = books[idx]

    if args.title is not None:
        book["title"] = args.title
    if args.author is not None:
        book["author"] = args.author
    if args.year is not None:
        book["year"] = args.year
    if args.genres is not None:
        book["genres"] = args.genres
    if args.in_stock is not None:
        book["in_stock"] = args.in_stock

    books[idx] = book
    save_books(books)
    print(f"Updated book id {args.id}")

def cmd_delete(args: argparse.Namespace) -> None:
    books = load_books()
    idx = get_book_index(books, args.id)
    deleted = books.pop(idx)
    save_books(books)
    print(f"Deleted book id {deleted['id']}")

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="CRUD for books.json")
    sub = p.add_subparsers(dest="command", required=True)

    sp_init = sub.add_parser("init", help="Create an empty books.json")
    sp_init.set_defaults(func=cmd_init)

    sp_list = sub.add_parser("list", help="List all books")
    sp_list.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    sp_list.set_defaults(func=cmd_list)

    sp_get = sub.add_parser("get", help="Get a single book by id")
    sp_get.add_argument("--id", type=int, required=True)
    sp_get.set_defaults(func=cmd_get)

    sp_add = sub.add_parser("add", help="Add a new book")
    sp_add.add_argument("--id", type=int, required=True)
    sp_add.add_argument("--title", required=True)
    sp_add.add_argument("--author", required=True)
    sp_add.add_argument("--year", type=int, required=True)
    sp_add.add_argument("--genres", nargs="*", default=[])
    stock_group = sp_add.add_mutually_exclusive_group()
    stock_group.add_argument("--in-stock", dest="in_stock", action="store_true")
    stock_group.add_argument("--out-of-stock", dest="in_stock", action="store_false")
    sp_add.set_defaults(in_stock=True, func=cmd_add)

    sp_upd = sub.add_parser("update", help="Update fields of a book by id")
    sp_upd.add_argument("--id", type=int, required=True)
    sp_upd.add_argument("--title")
    sp_upd.add_argument("--author")
    sp_upd.add_argument("--year", type=int)
    sp_upd.add_argument("--genres", nargs="*")
    stock_group2 = sp_upd.add_mutually_exclusive_group()
    stock_group2.add_argument("--in-stock", dest="in_stock", action="store_true")
    stock_group2.add_argument("--out-of-stock", dest="in_stock", action="store_false")
    sp_upd.set_defaults(in_stock=None, func=cmd_update)

    sp_del = sub.add_parser("delete", help="Delete a book by id")
    sp_del.add_argument("--id", type=int, required=True)
    sp_del.set_defaults(func=cmd_delete)

    return p

def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
