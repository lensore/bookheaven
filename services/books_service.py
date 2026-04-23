"""
Book storage service for BookHaven application.
Provides methods to retrieve book data.

Структура объекта книги:
id (str) — уникальный идентификатор
title (str) — название книги
author (str) — автор
price (float) — текущая цена
originalPrice (float, optional) — старая цена (если есть скидка)
imageUrl (str) — ссылка на обложку
badge (str, optional) — метка (например: Sale, New, Bestseller)
category (str) — категория/жанр
description (str) — краткое описание
"""


books_data = [
    {
        "id": "1",
        "title": "The Midnight Library",
        "author": "Matt Haig",
        "price": 14.99,
        "originalPrice": 19.99,
        "imageUrl": "https://images.unsplash.com/photo-1639954340684-9771e5e2ff47?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtb2Rlcm4lMjBmaWN0aW9uJTIwbm92ZWx8ZW58MXx8fHwxNzcxMzQ3OTM1fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
        "badge": "Sale",
        "category": "Fiction",
        "description": "A dazzling novel about all the choices that go into a life well lived.",
    },
    {
        "id": "2",
        "title": "Project Hail Mary",
        "author": "Andy Weir",
        "price": 16.99,
        "imageUrl": "https://images.unsplash.com/photo-1554357395-dbdc356ca5da?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzY2llbmNlJTIwZmljdGlvbiUyMGJvb2t8ZW58MXx8fHwxNzcxMjg1MDY1fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
        "badge": "Bestseller",
        "category": "Sci-Fi",
        "description": "A lone astronaut must save the earth from disaster in this incredible new science-based thriller.",
    },
    {
        "id": "3",
        "title": "The Silent Patient",
        "author": "Alex Michaelides",
        "price": 13.99,
        "imageUrl": "https://images.unsplash.com/photo-1698956483970-a47edef29331?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxteXN0ZXJ5JTIwdGhyaWxsZXIlMjBib29rfGVufDF8fHx8MTc3MTMwOTA3MXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
        "category": "Mystery",
        "description": "A woman's act of violence against her husband and her refusal to speak.",
    },
    {
        "id": "4",
        "title": "People We Meet on Vacation",
        "author": "Emily Henry",
        "price": 15.49,
        "originalPrice": 17.99,
        "imageUrl": "https://images.unsplash.com/photo-1711185901354-73cb6b666c32?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxyb21hbmNlJTIwbm92ZWwlMjBjb3ZlcnxlbnwxfHx8fDE3NzEzNDc5MzV8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
        "badge": "New",
        "category": "Romance",
        "description": "Two best friends. Ten summer trips. One last chance to fall in love.",
    },
    {
        "id": "5",
        "title": "Classic Tales Collection",
        "author": "Various Authors",
        "price": 24.99,
        "imageUrl": "https://images.unsplash.com/photo-1761319115156-d758b22ed57b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjbGFzc2ljJTIwbGl0ZXJhdHVyZSUyMGJvb2tzfGVufDF8fHx8MTc3MTMzODQ3N3ww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
        "category": "Classics",
        "description": "A timeless collection of the greatest stories ever told.",
    },
    {
        "id": "6",
        "title": "The Dragon Realm",
        "author": "Sarah J. Maas",
        "price": 18.99,
        "imageUrl": "https://images.unsplash.com/photo-1711185892188-13f35959d3ca?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxmYW50YXN5JTIwYm9vayUyMGNvdmVyfGVufDF8fHx8MTc3MTkyMjI4Nnww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
        "category": "Fantasy",
        "description": "An epic fantasy adventure filled with magic, dragons, and destiny.",
    },
    {
        "id": "7",
        "title": "Becoming",
        "author": "Michelle Obama",
        "price": 19.99,
        "imageUrl": "https://images.unsplash.com/photo-1582739010387-0b49ea2adaf6?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxiaW9ncmFwaHklMjBib29rfGVufDF8fHx8MTc3MTkyNTgwM3ww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
        "category": "Biography",
        "description": "A deeply personal memoir from the former First Lady of the United States.",
    },
    {
        "id": "8",
        "title": "Sapiens",
        "author": "Yuval Noah Harari",
        "price": 21.99,
        "imageUrl": "https://images.unsplash.com/photo-1758889468486-20d3f553ef57?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxoaXN0b3J5JTIwYm9vayUyMHZpbnRhZ2V8ZW58MXx8fHwxNzcxOTcwNDMxfDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
        "category": "History",
        "description": "A brief history of humankind from the Stone Age to the modern age.",
    },
]


def get_all_books():
    """Return all books."""
    return books_data


def get_books(category=None, sort=None, query=None):
    """Get books with optional category filter, search, and sorting."""
    books = list(books_data)

    if category:
        books = [book for book in books if book["category"] == category]

    if query:
        normalized_query = query.casefold()
        books = [
            book
            for book in books
            if normalized_query in book["title"].casefold()
            or normalized_query in book["author"].casefold()
        ]

    if sort == "price_asc":
        books.sort(key=lambda book: book["price"])
    elif sort == "price_desc":
        books.sort(key=lambda book: book["price"], reverse=True)

    return books


def get_book_by_id(book_id):
    """Get a book by ID."""
    for book in books_data:
        if book["id"] == str(book_id):
            return book
    return None


def get_books_by_category(category):
    """Get all books in a specific category."""
    return [book for book in books_data if book["category"] == category]


def get_featured_books(limit=4):
    """Get featured books and fill with regular books until limit."""
    featured = [book for book in books_data if book.get("badge")]
    if len(featured) >= limit:
        return featured[:limit]

    featured_ids = {book["id"] for book in featured}
    remaining = [book for book in books_data if book["id"] not in featured_ids]
    return (featured + remaining)[:limit]


def get_categories():
    """Get all unique categories."""
    categories = set()
    for book in books_data:
        categories.add(book["category"])
    return sorted(list(categories))
