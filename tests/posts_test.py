def test_cteate_post(client,auth_headers):
    response=client.post('/posts',json={
        'title':'тестовый пост',
        'content':'содержание поста'
    },headers=auth_headers
    )
    assert response.status_code==200
    data=response.json()
    assert data['title']=='тестовый пост'
    assert data['content']=='содержание поста'
    assert 'id' in data
    assert data['views']==0

def test_create_post_without_auth(client):
    response=client.post('/posts',
                         json={
                             'title':'пост',
                             'content':'содержание'
                         }
    )
    assert response.status_code==401

def test_get_all_posts(client,auth_headers):
    client.post('/posts',
                json={'title':'пост1','content':'содержание1'},
                headers=auth_headers
    )
    client.post('/posts',
                json={'title':'пост2','content':'содержание2'},
                headers=auth_headers
    )

    response=client.get('/posts')

    assert response.status_code==200
    data=response.json()
    assert isinstance(data,list)
    assert len(data)>=2

def test_get_single_post(client,auth_headers):
    create_response=client.post('/posts',
    json={'title':'тестовый пост','content':'содержание'
    },
    headers=auth_headers
    )
    post_id=create_response.json()['id']

    response=client.get(f'/posts/{post_id}')

    assert response.status_code==200
    data=response.json()
    assert data['id']==post_id
    assert data['title']=='тестовый пост'

def test_get_nonexistent_post(client):
    response=client.get('/posts/9999999999999999')
    assert response.status_code==404

def test_update_post(client,auth_headers):
    create_response=client.post('/posts',
    json={'title':'старый заголовок','content':'старое содержание'},
    headers=auth_headers
    )
    post_id=create_response.json()['id']

    response=client.patch(f'/posts/{post_id}',
    json={'title':'новый заголовок'},
    headers=auth_headers
    )

    assert response.status_code==200
    assert response.json()['title']=='новый заголовок'
    assert response.json()['content']=='старое содержание'

def test_delete_post(client,auth_headers):
    create_response=client.post('/posts',
    json={'title':'пост для удаления','content':'содержание'},
    headers=auth_headers
                                )
    post_id=create_response.json()['id']

    response=client.delete(f'/posts/{post_id}',headers=auth_headers)
    assert response.status_code==200
    assert 'deleted' in response.json()['message']

    get_response=client.get(f'/posts/{post_id}')
    assert get_response.status_code==404

