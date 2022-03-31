import csv

# from utils_newsfeed.models import PostManual
# from utils_newsfeed.models import NewsfeedBase

import utils_newsfeed.models as utm


def get_csv_data_size(file_path=None):
    with open(file_path, "r") as csv_file:
        data = csv.reader(csv_file, delimiter=",")
        next(data)
        index = 0
        for index, _ in enumerate(data):
            pass
        return index + 1


def load_csv(user=None, file_path=None, newsfeed_base_id=None):
    newsfeed_base = utm.NewsfeedBase.objects.filter(id=newsfeed_base_id).first()

    with open(file_path, "r") as csv_file:
        data = csv.reader(csv_file, delimiter=",")
        authors = {
            str(author.author): author for author in utm.Author.objects.all()
        }  # noqa: E501
        next(data)
        index = 0
        # posts = []
        for index, row in enumerate(data):
            author_agent_name = row[10].strip("'")
            author_agent = utm.AuthorAgent.objects.all().get(name=author_agent_name)
            verified_bare = row[15].strip("'")
            verified = True if verified_bare == "True" else False
            author_props = {
                "author_agent": author_agent,
                "author": row[11].strip("'"),
                "name": row[12].strip("'"),
                "avatar_url": row[13].strip("'"),
                "username": row[14].strip("'"),
                "verified": verified,
                "link": row[16].strip("'"),
            }
            authorId = row[11].strip("'")
            author = authors.get(authorId)
            if not author:
                author = utm.Author(**author_props)  # noqa: E501
                author.save()
                authors[author.author] = author

            post_props = {
                "user": user,
                "type": row[0].strip("'"),
                "author": author,
                "image_url": row[1].strip(" '"),
                "article_url": row[2].strip(" '"),
                "splash_image_url": row[3].strip(" '"),
                "header": row[4].strip("'"),
                "title": row[5].strip("'"),
                "content": row[6].strip("'"),
                "first_reaction": row[7].strip("'"),
                "second_reaction": row[8].strip("'"),
                "third_reaction": row[9].strip("'"),
            }
            if post_existing := utm.PostManual.objects.filter(**post_props).first():
                post_existing.newsfeed_base.add(newsfeed_base_id)
                newsfeed_base.post_order["order"][index] = post_existing.id
                newsfeed_base.post_order["value_to_key"][f"{post_existing.id}"] = index
                post_existing.save()
                continue

            post = utm.PostManual(**post_props)
            post.save()
            newsfeed_base.post_order["order"][index] = post.id
            newsfeed_base.post_order["value_to_key"][f"{post.id}"] = index

            post.newsfeed_base.add(newsfeed_base_id)

        # newsfeed_base.save()
        #     posts.append(post)
        #     if len(posts) > 5000:
        #         PostManual.objects.bulk_create(posts)
        #         posts = []
        # if posts:
        #     PostManual.objects.bulk_create(posts)


#
