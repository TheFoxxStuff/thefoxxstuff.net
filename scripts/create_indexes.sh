#!/bin/bash
# Создаёт MongoDB индексы для TheFoxxStuff
# Запускать ОДИН РАЗ после деплоя:
#   bash scripts/create_indexes.sh

echo "Creating MongoDB indexes..."

docker exec thefoxxstuff-mongo mongosh thefoxxstuff --quiet --eval '
// Music
db.music.createIndex({ release_date: -1 });
db.music.createIndex({ slug: 1 }, { unique: true, sparse: true });
db.music.createIndex({ is_new: 1, release_date: -1 });
db.music.createIndex({ views: -1 });

// Blog
db.blog.createIndex({ created_at: -1 });
db.blog.createIndex({ slug: 1 }, { unique: true, sparse: true });
db.blog.createIndex({ views: -1 });
db.blog.createIndex({ title: "text", content: "text" });

// Arts
db.arts.createIndex({ created_at: -1 });
db.arts.createIndex({ year: 1, created_at: -1 });
db.arts.createIndex({ slug: 1 }, { unique: true, sparse: true });
db.arts.createIndex({ views: -1 });

// Views
db.view_records.createIndex({ entity_type: 1, entity_id: 1, date: 1 }, { unique: true });
db.daily_views.createIndex({ entity_type: 1, date: 1 });

// IP views
db.ip_views.createIndex({ ip: 1, entity_type: 1, entity_id: 1, date: 1 }, { unique: true });
db.ip_views.createIndex({ date: 1 });
db.ip_views.createIndex({ timestamp: -1 });

// Chat
db.chat_messages.createIndex({ created_at: -1 });

// Users
db.users.createIndex({ username: 1 }, { unique: true });

print("All indexes created successfully!");
'
