def test_register_user(client):
    response=client.post('/users',json={
        'username':'bob',
        'email':'bob123@gmail.com',
        'password':'bobik123'
    })
    assert response.status_code==200

    data=response.json()
    assert data['username']=='bob'
    assert data['email']=='bob123@gmail.com'
    assert 'id' in data

def test_register_duplicate_user(client,test_user):
    first_response=client.post('/users',json={
        'username':'bob',
        'email':'bob123@gmail.com',
        'password':'bobik123'
    })

    assert first_response.status_code==200

    second_response=client.post('/users',json={
        'username':'bob',
        'email':'bob123@gmail.com',
        'password':'bobik123'
    })

    assert second_response.status_code==400

    assert 'already exists' in second_response.json()['detail']

def test_login_succes(client,test_user):
    response=client.post('/login',data={
        'username':'testuser',
        'password':'testpass123'
    })

    assert response.status_code==200
    assert 'access_token' in response.json()

def test_login_wrong_password(client,test_user):
    response=client.post('/login', data={
        'username':'testuser',
        'password':'123'
    })
    assert response.status_code==400
    assert 'Invalid' in response.json()['detail']

def test_get_current_user(client,test_user,auth_headers):
    response=client.get('/users/me',headers=auth_headers)
    assert response.status_code==200
    data=response.json()
    assert data['username']==test_user['username']
    assert data['email']==test_user['email']