from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from core.models import (
    City, Role, User, Community, Post, Comment,
    Chat, Message, Like, Friendship, UserCommunity, ChatParticipant
)


class Command(BaseCommand):
    help = 'Наполняет базу данных тестовыми данными для социальной сети'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить существующие данные перед добавлением'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Очистка существующих данных...')
            Message.objects.all().delete()
            ChatParticipant.objects.all().delete()
            Chat.objects.all().delete()
            Like.objects.all().delete()
            Comment.objects.all().delete()
            Post.objects.all().delete()
            UserCommunity.objects.all().delete()
            Friendship.objects.all().delete()
            Community.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            Role.objects.all().delete()
            City.objects.all().delete()

        self.stdout.write('Создание тестовых данных...')

        # Создаем города
        cities_data = [
            ('Москва', 'Россия'),
            ('Санкт-Петербург', 'Россия'),
            ('Новосибирск', 'Россия'),
            ('Екатеринбург', 'Россия'),
            ('Казань', 'Россия'),
            ('Нижний Новгород', 'Россия'),
            ('Самара', 'Россия'),
            ('Омск', 'Россия'),
            ('Ростов-на-Дону', 'Россия'),
            ('Краснодар', 'Россия'),
        ]
        cities = []
        for name, country in cities_data:
            city, _ = City.objects.get_or_create(name=name, country=country)
            cities.append(city)
        self.stdout.write(f'  Создано городов: {len(cities)}')

        # Создаем роли
        roles_data = [
            ('user', 'Обычный пользователь'),
            ('moderator', 'Модератор'),
            ('vip', 'VIP пользователь'),
        ]
        roles = []
        for name, desc in roles_data:
            role, _ = Role.objects.get_or_create(name=name, defaults={'description': desc})
            roles.append(role)
        self.stdout.write(f'  Создано ролей: {len(roles)}')

        # Создаем пользователей
        users_data = [
            ('ivan@example.com', 'Иван', 'Петров', 'ivan_petrov', 'male'),
            ('maria@example.com', 'Мария', 'Сидорова', 'maria_s', 'female'),
            ('alex@example.com', 'Александр', 'Козлов', 'alex_k', 'male'),
            ('elena@example.com', 'Елена', 'Новикова', 'elena_n', 'female'),
            ('dmitry@example.com', 'Дмитрий', 'Морозов', 'dmitry_m', 'male'),
            ('anna@example.com', 'Анна', 'Волкова', 'anna_v', 'female'),
            ('sergey@example.com', 'Сергей', 'Соловьев', 'sergey_s', 'male'),
            ('olga@example.com', 'Ольга', 'Лебедева', 'olga_l', 'female'),
            ('pavel@example.com', 'Павел', 'Кузнецов', 'pavel_k', 'male'),
            ('natalia@example.com', 'Наталья', 'Попова', 'natalia_p', 'female'),
            ('andrey@example.com', 'Андрей', 'Соколов', 'andrey_s', 'male'),
            ('ekaterina@example.com', 'Екатерина', 'Михайлова', 'kate_m', 'female'),
        ]

        users = []
        for email, first, last, username, gender in users_data:
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    email=email,
                    password='testpass123',
                    first_name=first,
                    last_name=last,
                    username=username,
                    gender=gender,
                    city=random.choice(cities),
                    role=random.choice(roles),
                    bio=f'Привет! Меня зовут {first}. Рад(а) знакомству!',
                    is_online=random.choice([True, False]),
                    is_verified=random.choice([True, False]),
                    birth_date=timezone.now().date() - timedelta(days=random.randint(7000, 15000)),
                    last_seen=timezone.now() - timedelta(hours=random.randint(0, 72))
                )
                users.append(user)
            else:
                users.append(User.objects.get(email=email))
        self.stdout.write(f'  Создано пользователей: {len(users)}')

        # Создаем дружбу между пользователями
        friendships_created = 0
        for i, user in enumerate(users):
            # Каждый пользователь дружит с 2-4 другими
            friends_count = random.randint(2, 4)
            potential_friends = [u for u in users if u != user]
            for friend in random.sample(potential_friends, min(friends_count, len(potential_friends))):
                # Проверяем, нет ли уже дружбы
                exists = Friendship.objects.filter(
                    user=user, friend=friend
                ).exists() or Friendship.objects.filter(
                    user=friend, friend=user
                ).exists()
                if not exists:
                    Friendship.objects.create(
                        user=user,
                        friend=friend,
                        status='accepted',
                        created_by=user
                    )
                    friendships_created += 1
        self.stdout.write(f'  Создано дружб: {friendships_created}')

        # Создаем несколько заявок в друзья (pending)
        pending_requests = 0
        for _ in range(5):
            user = random.choice(users)
            friend = random.choice([u for u in users if u != user])
            exists = Friendship.objects.filter(
                user=user, friend=friend
            ).exists() or Friendship.objects.filter(
                user=friend, friend=user
            ).exists()
            if not exists:
                Friendship.objects.create(
                    user=user,
                    friend=friend,
                    status='pending',
                    created_by=user
                )
                pending_requests += 1
        self.stdout.write(f'  Создано заявок в друзья: {pending_requests}')

        # Создаем сообщества
        communities_data = [
            ('Программисты Python', 'Сообщество для Python разработчиков. Делимся опытом и знаниями.', 'open'),
            ('Любители кино', 'Обсуждаем фильмы, сериалы и все, что связано с кинематографом.', 'open'),
            ('Путешественники', 'Для тех, кто любит путешествовать. Делимся впечатлениями и советами.', 'open'),
            ('Фотографы', 'Сообщество фотографов. Критика, советы, обмен опытом.', 'open'),
            ('Книжный клуб', 'Обсуждаем прочитанные книги и делимся рекомендациями.', 'closed'),
            ('Геймеры', 'Для любителей компьютерных игр. Обзоры, обсуждения, поиск тиммейтов.', 'open'),
            ('Музыканты', 'Сообщество музыкантов. Делимся творчеством и ищем коллабы.', 'closed'),
            ('Спортсмены', 'Здоровый образ жизни, тренировки, мотивация.', 'open'),
        ]

        communities = []
        for name, desc, type_ in communities_data:
            owner = random.choice(users)
            community, created = Community.objects.get_or_create(
                name=name,
                defaults={
                    'description': desc,
                    'type': type_,
                    'owner': owner,
                    'created_by': owner,
                    'is_verified': random.choice([True, False])
                }
            )
            communities.append(community)

            # Добавляем участников
            if created:
                UserCommunity.objects.create(
                    user=owner,
                    community=community,
                    role='admin',
                    created_by=owner
                )
                members = random.sample([u for u in users if u != owner], random.randint(3, 7))
                for member in members:
                    UserCommunity.objects.create(
                        user=member,
                        community=community,
                        role='member',
                        created_by=member
                    )
                community.members_count = len(members) + 1
                community.save()
        self.stdout.write(f'  Создано сообществ: {len(communities)}')

        # Создаем посты
        posts_content = [
            'Всем привет! Сегодня отличный день для новых начинаний!',
            'Поделюсь интересной статьей, которую недавно прочитал. Очень познавательно!',
            'Кто-нибудь знает хороший ресторан в центре города? Ищу место для встречи с друзьями.',
            'Только что закончил новый проект! Столько сил вложено, но результат того стоит.',
            'Смотрю сейчас потрясающий сериал. Кто уже видел - без спойлеров, пожалуйста!',
            'Выходные прошли продуктивно. Успел и поработать, и отдохнуть.',
            'Интересно, как вы справляетесь со стрессом? Поделитесь советами в комментариях.',
            'Сегодня начал изучать новый язык программирования. Никогда не поздно учиться!',
            'Прекрасная погода за окном! Самое время для прогулки в парке.',
            'Приготовил сегодня новое блюдо по рецепту из интернета. Получилось даже лучше, чем ожидал!',
            'Читаю сейчас невероятную книгу. Не могу оторваться!',
            'Кто хочет присоединиться к онлайн-тренировке? Начинаем в 18:00!',
            'Завершил марафон! 42 км позади, но эмоции переполняют.',
            'Новый альбом любимой группы - просто огонь! Рекомендую всем.',
            'Сходил на выставку современного искусства. Впечатления неоднозначные, но интересно.',
        ]

        posts = []
        for _ in range(30):
            author = random.choice(users)
            community = random.choice(communities + [None, None, None])  # 50% без сообщества

            post = Post.objects.create(
                author=author,
                community=community,
                content=random.choice(posts_content),
                views_count=random.randint(10, 500),
                is_published=True,
                created_by=author,
                created_at=timezone.now() - timedelta(days=random.randint(0, 30))
            )
            posts.append(post)
        self.stdout.write(f'  Создано постов: {len(posts)}')

        # Создаем комментарии
        comments_content = [
            'Полностью согласен!',
            'Интересная мысль, надо подумать.',
            'Спасибо за пост!',
            'А можно подробнее?',
            'Круто! Поддерживаю!',
            'Не совсем согласен, но уважаю твое мнение.',
            'Отличный пост, спасибо что делишься!',
            'Это точно! Сам недавно думал об этом.',
            'Классно написано!',
            'Жду продолжения!',
        ]

        comments_created = 0
        for post in posts:
            for _ in range(random.randint(0, 5)):
                author = random.choice(users)
                Comment.objects.create(
                    post=post,
                    author=author,
                    content=random.choice(comments_content),
                    created_by=author,
                    created_at=post.created_at + timedelta(hours=random.randint(1, 48))
                )
                comments_created += 1
        self.stdout.write(f'  Создано комментариев: {comments_created}')

        # Создаем лайки
        likes_created = 0
        for post in posts:
            likers = random.sample(users, random.randint(2, 8))
            for user in likers:
                Like.objects.get_or_create(
                    user=user,
                    post=post
                )
                likes_created += 1
        self.stdout.write(f'  Создано лайков: {likes_created}')

        # Создаем личные чаты
        private_chats = []
        for i in range(10):
            user1, user2 = random.sample(users, 2)
            # Проверяем, нет ли уже чата между этими пользователями
            existing = Chat.objects.filter(
                type='private',
                participants__user=user1
            ).filter(
                participants__user=user2
            ).first()

            if not existing:
                chat = Chat.objects.create(
                    type='private',
                    created_by=user1
                )
                ChatParticipant.objects.create(chat=chat, user=user1, role='member')
                ChatParticipant.objects.create(chat=chat, user=user2, role='member')
                private_chats.append((chat, user1, user2))
        self.stdout.write(f'  Создано личных чатов: {len(private_chats)}')

        # Создаем групповые чаты
        group_chats = []
        group_chat_names = [
            'Рабочий чат',
            'Друзья навсегда',
            'Планируем выходные',
            'Киноманы',
        ]
        for name in group_chat_names:
            creator = random.choice(users)
            chat = Chat.objects.create(
                name=name,
                type='group',
                created_by=creator
            )
            ChatParticipant.objects.create(chat=chat, user=creator, role='admin')
            members = random.sample([u for u in users if u != creator], random.randint(3, 6))
            for member in members:
                ChatParticipant.objects.create(chat=chat, user=member, role='member')
            group_chats.append(chat)
        self.stdout.write(f'  Создано групповых чатов: {len(group_chats)}')

        # Создаем сообщения в чатах
        messages_content = [
            'Привет!',
            'Как дела?',
            'Отлично, спасибо!',
            'Что делаешь?',
            'Ничего особенного, отдыхаю.',
            'Давно не виделись!',
            'Да, надо бы встретиться.',
            'Когда ты свободен?',
            'На выходных можно.',
            'Отлично, договорились!',
            'Смотрел новый фильм?',
            'Да, очень понравился!',
            'Надо будет тоже посмотреть.',
            'Рекомендую!',
            'Спасибо за совет!',
        ]

        messages_created = 0
        # Сообщения в личных чатах
        for chat, user1, user2 in private_chats:
            participants = [user1, user2]
            for i in range(random.randint(5, 15)):
                sender = participants[i % 2]
                Message.objects.create(
                    chat=chat,
                    sender=sender,
                    content=random.choice(messages_content),
                    status='read' if random.random() > 0.3 else 'sent',
                    created_by=sender,
                    created_at=timezone.now() - timedelta(hours=random.randint(0, 72))
                )
                messages_created += 1

        # Сообщения в групповых чатах
        for chat in group_chats:
            participants = list(chat.participants.values_list('user', flat=True))
            participant_users = User.objects.filter(id__in=participants)
            for _ in range(random.randint(10, 25)):
                sender = random.choice(list(participant_users))
                Message.objects.create(
                    chat=chat,
                    sender=sender,
                    content=random.choice(messages_content),
                    status='read' if random.random() > 0.3 else 'sent',
                    created_by=sender,
                    created_at=timezone.now() - timedelta(hours=random.randint(0, 72))
                )
                messages_created += 1

        self.stdout.write(f'  Создано сообщений: {messages_created}')

        self.stdout.write(self.style.SUCCESS('\nТестовые данные успешно созданы!'))
        self.stdout.write('\nДля входа используйте:')
        self.stdout.write('  Email: ivan@example.com')
        self.stdout.write('  Пароль: testpass123')
        self.stdout.write('\n(или любой другой email из списка с тем же паролем)')
