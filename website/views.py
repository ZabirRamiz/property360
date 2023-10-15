from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib import messages
from datetime import datetime, timedelta
# from website.models import User
from django.db import connection
# Create your views here.


def createUser(n):
    if len(str(n)) < 4:
        # return ("user_"+("0"*(4-len(str(n)))) + str(n))
        s = ("user_"+("0"*(4-len(str(n)))) + str(n))

        existing_user = 'select user_id from website_user order by user_id asc'
        user_tuple = ''
        with connection.cursor() as cursor:
            cursor.execute(existing_user)
            user_tuple = list(cursor.fetchall())
        # print('-------/////////////////--------------',user_tuple,s)
        if (s,) in user_tuple:
            s = createUser(n+1)

        return s

    else:
        return "user_"+str(n)


def createAgent(n):
    if len(str(n)) < 4:
        # return ("agent_"+("0"*(4-len(str(n)))) + str(n))
        s = ("agent_"+("0"*(4-len(str(n)))) + str(n))

        existing_agent = 'select agent_id from website_agent order by agent_id asc'
        agent_tuple = ''
        with connection.cursor() as cursor:
            cursor.execute(existing_agent)
            agent_tuple = list(cursor.fetchall())
        # print('-------/////////////////--------------',agent_tuple,s)
        if (s,) in agent_tuple:
            s = createAgent(n+1)

        return s

    else:
        return "agent_"+str(n)


def createProp(n):
    s = ''
    # print("/////////////////////createprop///////////////////")
    if len(str(n)) < 4:
        s = ("prop_"+("0"*(4-len(str(n)))) + str(n))

        existing_prop = 'select property_id from website_property order by property_id asc'
        prop_tuple = ''
        with connection.cursor() as cursor:
            cursor.execute(existing_prop)
            prop_tuple = list(cursor.fetchall())
        # print('-------/////////////////--------------',prop_tuple,s)
        if (s,) in prop_tuple:
            s = createProp(n+1)

        return s
    else:
        return "prop_"+str(n)


def createAuct(n):
    s = ''
    # print("/////////////////////createprop///////////////////")
    if len(str(n)) < 4:
        s = ("auct_"+("0"*(4-len(str(n)))) + str(n))

        existing_auct = 'select auction_id from website_auction order by auction_id asc'
        auct_tuple = ''
        with connection.cursor() as cursor:
            cursor.execute(existing_auct)
            auct_tuple = list(cursor.fetchall())
        # print('-------/////////////////--------------',auct_tuple,s)
        if (s,) in auct_tuple:
            s = createAuct(n+1)

        return s
    else:
        return "auct_"+str(n)


def sessionInfo():
    retrieve_login = "select * from website_session"
    with connection.cursor() as cursor:
        cursor.execute(retrieve_login)
        temp = tuple(cursor.fetchall())[0]
        return temp


def setLogin(user):
    setlogin = "update website_session set user=%s, login = 'True' where user='user_0000'"
    with connection.cursor() as cursor:
        cursor.execute(setlogin, [user])


def fetch_property(request):
    info = sessionInfo()
    if '0000' in info[0]:
        messages.warning(request, 'Login To Continue')
        return redirect('login')
    user = info[0]
    if 'user' in user:
        if request.method == "POST":
            property_id = request.POST['property_id']
            request.session['property_id'] = property_id
        return redirect('property_edit_info')
    elif "agent" in user:
        if request.method == 'POST':
            property_id = request.POST['property_id']
            update_status = "update website_property set status = 'For Sale' where property_id = %s "
            with connection.cursor() as cursor:
                cursor.execute(update_status, [property_id])
                messages.success(request, 'Property Added To Market')
            request.session['property_id'] = property_id
        return redirect('dashboard')


def setLogout():
    setlogout = "update website_session set user='user_0000', login = 'False' where login='True'"
    with connection.cursor() as cursor:
        cursor.execute(setlogout)


def login(request):
    return render(request, 'login.html')


def logout(request):
    setLogout()
    return redirect('/')


def user(request):
    usertype = "user"
    info = sessionInfo()
    if request.method == "POST":  # if signup form filled
        name = request.POST['name']
        email = request.POST['email']
        password1 = request.POST['pswd1']
        password2 = request.POST['pswd2']
        phone = request.POST['phone']
        print(phone)
        psswd = None
        if password1 == password2:
            psswd = password1
        else:
            messages.warning(request, "Please retype the password properly")
            return redirect('login')
        if '@property360.agent.com' in email:
            usertype = "agent"
            print("USER AGENT")

        addrss = request.POST['address']
        data = {
            'user_name': name,
            'user_email': email,
            'user_address': addrss
        }
        find_agent = "select employee_id from website_employee where employee_id like 'agent%'"
        find_user = "select user_id from website_user where user_id like 'user%'"
        insert_user = 'insert into website_user (user_id, username, email, password, address,auction_status,phone) values (%s, %s, %s, %s, %s,%s,%s)'
        insert_emp = 'insert into website_employee (employee_id, name, phone, email, password, address,supervisor) values (%s, %s, %s, %s, %s, %s, %b) '
        with connection.cursor() as cursor:
            uid = ""
            if usertype == "user":
                cursor.execute(find_user)
                user_list = tuple(cursor.fetchall())
                # print(user_list)
                entries = len(user_list)
                uid = createUser((entries+1))
                cursor.execute(insert_user, (uid, name, email,
                               psswd, addrss, 'not_joined', phone))
            else:
                cursor.execute(find_agent)
                agent_list = tuple(cursor.fetchall())
                # print(agent_list)
                entries = len(agent_list)
                uid = createAgent((entries+1))
                cursor.execute(
                    insert_emp, (uid, name, phone, email, psswd, addrss, 0))
            setLogin(uid)

        data.update({'user_id': sessionInfo()[0]})
        messages.success(request, 'Signup Successful')
        return render(request, 'user.html', data)

    return render(request, 'user.html')
    # return render(request, 'user.html', {'user_id': info[0]})


def agent_dashboard(request):
    info = sessionInfo()
    user = info[0]
    if info[1] == 'True':
        return render(request, 'agent_dashboard.html', {'user': user})
    # return render(request, 'user.html')


def dashboard(request):
    info = sessionInfo()
    if info[1] == 'True':
        if 'agent' in info[0]:
            get_agent = 'select employee_id, name, email, address, phone, supervisor_id, agent_img from website_employee, website_agent where agent_id_id=employee_id and employee_id=%s'
            get_prop = 'select property_id,status,location,name,size,type,price,property_img,user_id_id,agent_id_id from website_property where agent_id_id=%s'
            agent_temp = ''
            agent_prop = ''
            # staring work on activity

            agent = info[0]
            with connection .cursor() as cursor:
                cursor.execute(get_agent, [agent])
                agent_temp = tuple(cursor.fetchall())[0]
                cursor.execute(get_prop, [agent])
                agent_prop = tuple(cursor.fetchall())

            agent_data = {
                'agent_id': info[0],
                'agentname': agent_temp[1],
                'email': agent_temp[2],
                'address': agent_temp[3],
                'phone': agent_temp[4],
                'supervisor_id': agent_temp[5],
                'agent_img': agent_temp[6],
                'prop': agent_prop,
                # 'all_prop': all_prop,
            }

            print(agent_data)
            # return render(request, 'agent_dashboard.html',  agent_data)
            return render(request, 'agent_dashboard.html',  {'user_id': info[0], 'data': agent_data})

        #  admin dashboard
        if 'adm' in info[0]:
            # get_admin= 'select employee_id, name, email, address, phone, supervisor_id, agent_img from website_employee, website_agent where agent_id_id=employee_id and employee_id=%s'
            get_admin = 'select admin_id, name, email from website_admin where admin_id=%s'
            # get_prop = 'select property_id,status,location,name,size,type,price,property_img,user_id_id,agent_id_id from website_property where agent_id_id=%s'
            admin_temp = ''
            # admin_prop = ''
            # staring work on activity
            total_employee = 'select count(*) from website_employee'
            t_emp = ''
            total_property = 'select count(*) from website_property'
            t_property = ''
            total_user = 'select count(*) from website_user'
            t_user = ''

            auction_status = 'select auction_status from website_auction'
            a_status = ''

            admin = info[0]
            with connection.cursor() as cursor:
                cursor.execute(get_admin, [admin])
                admin_temp = tuple(cursor.fetchall())[0]
                # cursor.execute(get_prop,[admin])
                # admin_prop = tuple(cursor.fetchall())
                cursor.execute(total_employee)
                t_emp = tuple(cursor.fetchall())[0]
                cursor.execute(total_property)
                t_property = tuple(cursor.fetchall())[0]
                cursor.execute(total_user)
                t_user = tuple(cursor.fetchall())[0]

                cursor.execute(auction_status)

                a_status = tuple(cursor.fetchall())
                if len(a_status) == 0:
                    a_status = "No Auction Active"
                else:
                    a_status = "Active"
            admin_data = {
                'admin_id': info[0],
                'adminname': admin_temp[1],
                'email': admin_temp[2],
                't_emp': t_emp,
                't_user': t_user,
                't_property': t_property,
                'a_status': a_status,
            }

            print(admin_data)
            # return render(request, 'agent_dashboard.html',  agent_data)
            return render(request, 'admin_dashboard.html',  {'user_id': info[0], 'data': admin_data})

        # user dashboard
        elif 'user' in info[0]:
            user = info[0]
            get_user = 'select user_id, username, email, address,user_img from website_user where user_id=%s'
            get_prop = 'select property_id,status,location,name,size,type,price,property_img,user_id_id,agent_id_id from website_property where user_id_id=%s order by property_id '
            user_temp = ''
            user_prop = ''
            # starting work on activity
            get_property_and_status = 'select property_id, status from website_property where user_id_id = %s'
            prop_status = ''
            get_property_and_agent = "select property_id, agent_id_id from website_property where user_id_id =%s and agent_id_id != 'agent_0000'"
            prop_agent = ''
            get_auction_property_and_price = "select property_id_id, starting_price, selling_price from website_auction_property where owner_id_id = %s "
            auction_prop_price = ''
            # get_property_and_support = "select hires.property_id_id, hires.support_id_id, support.type  from website_hires hires, website_support support where hires.support_id_id = support.support_id_id order by hires.support_id_id"
            get_property_and_support = "select hires.property_id_id, hires.support_id_id, support.type  from website_hires hires, website_support support where hires.support_id_id = support.support_id_id and hires.user_id_id = %s"
            prop_support = ''
            with connection.cursor() as cursor:
                cursor.execute(get_user, [user])
                user_temp = tuple(cursor.fetchall())[0]
                cursor.execute(get_prop, [user])
                user_prop = tuple(cursor.fetchall())

                cursor.execute(get_property_and_status, [user])
                prop_status = tuple(cursor.fetchall())
                cursor.execute(get_property_and_agent, [user])
                prop_agent = tuple(cursor.fetchall())
                cursor.execute(get_auction_property_and_price, [user])
                auction_prop_price = tuple(cursor.fetchall())
                cursor.execute(get_property_and_support, [user])
                prop_support = tuple(cursor.fetchall())

            user_data = {
                'user_id': info[0],
                'username': user_temp[1],
                'email': user_temp[2],
                'address': user_temp[3],
                'user_img': user_temp[4],
                'prop': user_prop,
                'prop_status': prop_status,
                'prop_agent': prop_agent,
                'prop_support': prop_support,
                'auction_prop_price': auction_prop_price,
            }
            print(user_data)
            return render(request, 'user.html', user_data)
            # return render(request, 'user.html',  {'user_id':info[0],'data': user_data})

    return render(request, 'user.html')


def login_user(request):
    user = None
    password = None
    if request.method == "POST":
        user = request.POST['uid']
        retrieve_pass = ''
        retrieve_name = ''
        if 'user' in user:
            retrieve_pass = "select password from website_user where user_id= %s"
            retrieve_name = "select username from website_user where user_id = %s"
        elif 'agent' in user:
            retrieve_pass = "select password from website_employee where employee_id= %s"
            retrieve_name = "select name from website_employee where employee_id = %s"
        elif 'adm' in user:
            retrieve_pass = "select password from website_admin where admin_id= %s"
            retrieve_name = "select name from website_admin where admin_id = %s"
        password = request.POST['pswd']
        pass_data = ""
        name_data = ""
        with connection.cursor() as cursor:
            cursor.execute(retrieve_pass, [user])
            pass_data = tuple(cursor.fetchall())[0][0]
            cursor.execute(retrieve_name, [user])
            name_data = tuple(cursor.fetchall())[0][0]
        if pass_data == password:
            setLogin(user)
            info = sessionInfo()
            arg = {'user_id': info[0], 'user_name': name_data}
    return redirect('dashboard')


def agents(request):
    info = sessionInfo()
    login_info = info[1]
   # EXCLUDED AGENT_0000
    agent_retrieve = "select agent_id_id, supervisor_id ,name, email ,phone, address, supervisor from website_agent,website_employee where agent_id_id =employee_id and agent_id_id like 'agent%' and agent_id_id <> 'agent_0000' order by agent_id_id"
    agent_data = None
    seller_retrieve = 'select agent_id_id from  website_seller where seller_id_id=%s'
    supervisor_data = "select employee_id from website_employee where employee_id like 'agent%' and employee_id <> 'agent_0000' and supervisor=1"
    supervisor_list = ''
    seller_agent_data = ''
    with connection.cursor() as cursor:
        cursor.execute(agent_retrieve)
        agent_data = list(tuple(cursor.fetchall()))
        cursor.execute(supervisor_data)
        supervisor_list = tuple(cursor.fetchall())
        cursor.execute(seller_retrieve, [info[0]])
        seller_agent_data = tuple(cursor.fetchall())
    for agent in agent_data:
        temp_agent = list(agent)
        if any(temp_agent[0] in hired for hired in seller_agent_data):
            temp_agent.append('Hired')
        else:
            temp_agent.append('Not_Hired')
        i = agent_data.index(agent)
        agent_data[i] = tuple(temp_agent)
    agent_data = tuple(agent_data)

    if info[1] == "True":
        return render(request, 'agents.html', {'user_id': info[0], 'data': agent_data, 'supervisor_data': supervisor_list})
    else:

        return render(request, 'agents.html', {'data': agent_data})


def make_supervisor(request):
    info = sessionInfo()
    agent = request.POST['agent_id']
    make_sup = 'update website_employee set supervisor=%b where employee_id=%s'
    get_pass = 'select password from website_admin where admin_id = %s'
    adm_pass = request.POST['confirm_password']
    password = ''
    with connection.cursor() as c:
        c.execute(get_pass, [info[0]])
        password = tuple(c.fetchall())
        if len(password) > 0:
            password = password[0][0]
        else:
            password = ''
        if adm_pass == password:

            c.execute(make_sup, (1, agent))
            messages.success(request, f"Agent {agent} promoted to Supervisor")
        else:
            messages.warning(request, 'Plese Enter correct password')

    return redirect('agents')


def remove_supervisor(request):
    info = sessionInfo()
    agent = request.POST['agent_id']
    make_sup = 'update website_employee set supervisor= 0 where employee_id=%s'
    get_pass = 'select password from website_admin where admin_id = %s'
    change_supervisor = "update website_agent set supervisor_id='agent_0000' where supervisor_id=%s"
    adm_pass = request.POST['confirm_password']
    password = ''
    with connection.cursor() as c:
        c.execute(get_pass, [info[0]])
        password = tuple(c.fetchall())
        if len(password) > 0:
            password = password[0][0]
        else:
            password = ''
        if adm_pass == password:
            c.execute(change_supervisor, [agent])
            c.execute(make_sup, [agent])
            messages.warning(request, f"Agent {agent} demoted from Supervisor")
        else:
            messages.warning(request, 'Plese Enter correct password')

    return redirect('agents')


def set_supervisor(request):
    info = sessionInfo()
    if request.method == "POST":
        supervisor_id = request.POST['supv_id']
        agent_id = request.POST['agent_id']
        print(supervisor_id, 'supervisor')
        print(agent_id, 'agent')
        set_supervisor = 'update website_agent set supervisor_id=%s where agent_id_id=%s'
        with connection.cursor() as c:
            c.execute(set_supervisor, (supervisor_id, agent_id))
            messages.success(
                request, f"{supervisor_id} set Supervisor for {agent_id}")
    return redirect('agents')


def about(request):
    info = sessionInfo()
    login_info = info[1]
    if info[1] == "True":
        return render(request, 'about.html', {'user_id': info[0]})
    else:
        return render(request, 'about.html')


def property(request):
    info = sessionInfo()
    login_info = info[1]
    user = info[0]
    property_retrieve = " select property_id,status,location,name,size,type,price,property_img,user_id_id,agent_id_id from website_property where status = 'For Sale' order by property_id"
    # property_retrieve = "select property_id, name,agent_id_id, location, size, type, price, status from website_property where status = 'For Sale'"
    property_data = None
    with connection.cursor() as cursor:
        cursor.execute(property_retrieve)
        property_data = tuple(cursor.fetchall())
    # print(property_data)

    if info[1] == 'True':
        return render(request, 'property.html', {'data': property_data, 'user_id': user})

    return render(request, 'property.html', {'data': property_data})


def buy_property(request):
    info = sessionInfo()
    login_info = info[1]
    user = info[0]
    if request.method == "POST":
        property_id = request.POST['property_id']
        check_owner = "select user_id_id from website_property where property_id = %s"
        owner = ''
        with connection.cursor() as cursor:
            cursor.execute(check_owner, [property_id])
            owner = tuple(cursor.fetchall())[0]
        if user not in owner:

            password = request.POST['password']
            retrieve_password = 'select password from website_user where user_id = %s'
            confirm_password = ''
            with connection.cursor() as cursor:
                cursor.execute(retrieve_password, [user])
                confirm_password = tuple(cursor)[0][0]

            if password == confirm_password:
                update_owner = "update website_property set user_id_id = %s, status = 'Not For Sale', agent_id_id = 'agent_0000' where property_id = %s"
                with connection.cursor() as cursor:
                    cursor.execute(update_owner, (user, property_id))
                    messages.success(request, "Successfully Bought Property")

            else:
                messages.warning(request, 'Incorrect Password')

        else:
            messages.warning(request, "Already Owned")
            return redirect('property')
        # else:
    return redirect('property')


def support(request):
    info = sessionInfo()
    login_info = info[1]
    user = info[0]
    print(user)
    property_retrieve = "select property_id from website_property where user_id_id=%s"
    property_list = None
    support_retrieve = "select name, type, phone, hiring_price, support_id_id from website_support s, website_employee e where e.employee_id = s.support_id_id"
    support_data = None
    with connection.cursor() as cursor:
        cursor.execute(support_retrieve)
        support_data = tuple(cursor.fetchall())
        cursor.execute(property_retrieve, [user])
        property_list = tuple(cursor.fetchall())
    if info[1] == "True":
        return render(request, 'support.html', {'data': support_data, 'property_list': property_list, 'user_id': info[0]})

    else:
        return render(request, 'support.html', {'data': support_data})


def property_registration(request):
    info = sessionInfo()
    login_info = info[1]
    user = info[0]
    if info[1] == "True":
        agent_list = ''
        with connection.cursor() as cursor:
            cursor.execute(
                "select employee_id,name from website_employee where employee_id like 'agent%'")
            agent_list = tuple(cursor.fetchall())
        # print(agent_list)
        return render(request, 'property_registration.html', {'user_id': info[0], 'agents': agent_list})

    else:
        return render(request, 'property_registration.html')


def propertyId_submit(request):
    info = sessionInfo()
    login_info = info[1]
    user = info[0]
    if info[1] == "True":
        if request.method == 'POST':
            agent_id = request.POST['agent_id']
            property_list = ''
            find_property = 'select property_id from website_property where user_id_id=%s and agent_id_id<>%s '
            with connection.cursor() as cursor:
                cursor.execute(find_property, (user, agent_id))
                property_list = tuple(cursor.fetchall())
            dic = {
                'user_id': info[0],
                'agent_id': agent_id,
                'properties': property_list
            }
            return render(request, 'propertyId_submit.html', dic)
    else:
        return render(request, 'propertyId_submit.html')


def hire_agent(request):
    info = sessionInfo()
    if '0000' in info[0]:
        messages.warning(request, 'Login to continue')
        return redirect('login')
    login_info = info[1]
    user = info[0]
    if request.method == 'POST':
        password = request.POST['confirm_password']
        property_id = request.POST['prop_id']
        agent_id = request.POST['agent_id']
        password1 = ''
        user_id = ''
        retrieve_pass = 'select password from website_user where user_id= %s'
        retrieve_user_id = 'select user_id_id from website_property where property_id=%s'
        update_agent = "update website_property set agent_id_id=%s, status ='Available For Market' where property_id=%s"
        insert_seller = 'insert into website_seller (seller_id_id,hiring_price ,agent_id_id) values (%s,%s,%s)'
        with connection.cursor() as cursor:
            cursor.execute(retrieve_pass, [user])
            password1 = tuple(cursor.fetchall())[0][0]
            cursor.execute(retrieve_user_id, [property_id])
            user_id = tuple(cursor.fetchall())[0][0]
            if password == password1 and user == user_id:
                cursor.execute(update_agent, (agent_id, property_id))
                cursor.execute(insert_seller, (user, '0000', agent_id))
                messages.success(request, "Agent Hired Successfully")
            else:
                messages.warning(request, "Incorrect Password")

    return redirect('agents')
    # return redirect('dashboard')


def agent_remove(request):
    info = sessionInfo()
    if '0000' in info[0]:
        messages.warning(request, 'Login to continue')
        return redirect('login')
    login_info = info[1]
    user = info[0]
    if request.method == 'POST':
        password = request.POST['confirm_password']
        property_id = request.POST['prop_id']
        agent_id = request.POST['agent_id']
        password1 = ''
        retrieve_pass = 'select password from website_user where user_id= %s'
        update_agent = "update website_property set agent_id_id='agent_0000' , status = 'Not For Sale' where property_id=%s"
        delete_seller = 'delete from  website_seller where agent_id_id=%s'

        with connection.cursor() as cursor:
            cursor.execute(retrieve_pass, [user])
            password1 = tuple(cursor.fetchall())[0][0]
            if password == password1:
                cursor.execute(update_agent, [property_id])
                cursor.execute(delete_seller, [agent_id])
                messages.success(request, "Agent_Id Remove")
    return redirect('agents')


def remove_propertyId_submission(request):
    info = sessionInfo()
    login_info = info[1]
    user = info[0]
    if info[1] == "True":
        if request.method == 'POST':
            agent_id = request.POST['agent_id']
            property_list = ''
            find_property = 'select property_id from website_property where user_id_id=%s and agent_id_id=%s '
            with connection.cursor() as cursor:
                cursor.execute(find_property, (user, agent_id))
                property_list = tuple(cursor.fetchall())
            dic = {
                'user_id': info[0],
                'agent_id': agent_id,
                'properties': property_list
            }
            return render(request, 'remove_propertyId_submission.html', dic)
    else:
        return render(request, 'remove_propertyId_submission.html')


def property_save(request):
    info = sessionInfo()
    login_info = info[1]
    user = info[0]
    if request.method == 'POST':
        name = request.POST['property_name']
        location = request.POST['location']
        size = request.POST['size']
        price = request.POST['price']
        # status = request.POST['status']
        type = request.POST['type']
        image = request.FILES['property_img']
        # prop_agent = request.POST['hired_agent']
        # print(prop_agent,'-----------23423423')
        with open('media/' + image.name, 'wb') as f:
            for chunk in image.chunks():
                f.write(chunk)
        all_properties = 'select property_id from website_property'
        with connection.cursor() as cursor:
            cursor.execute(all_properties)
            property_tuple = tuple(cursor.fetchall())
            entries = len(property_tuple)
            # print(entries)
            property_id = createProp((entries+1))
            # print(property_id)

        # property_insert = "INSERT INTO website_property(property_id, status, location, name, size, type, price, property_img, user_id_id, agent_id_id) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        property_insert = "INSERT INTO website_property(property_id, location, name, size, type, price, property_img, user_id_id, agent_id_id, status) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        with connection.cursor() as cursor:
            # cursor.execute(property_insert, (property_id, status, location, name, size, type, price,image.name, user,prop_agent))
            cursor.execute(property_insert, (property_id, location, name, size,
                           type, price, image.name, user, 'agent_0000', 'Not For Sale'))
            messages.success(request, "Property Submitted")
    # return redirect('dashboard')
    return render(request, 'property_registration.html', {'user_id': user})


def property_list(request):
    info = sessionInfo()
    login_info = info[1]
    user = info[0]
    property_retrieve = "select image, property_id, name, size, type, price, agent_id_id, status from website_property where user_id_id = %s"
    property_data = None

    with connection.cursor() as cursor:
        cursor.execute(property_retrieve, user)
        property_data = tuple(cursor.fetchall())[0]

    return redirect('support')
    # if info[1]=="True":
    #     return render(request, 'user.html', {'data': property_data,'user_id':user})
    # else:
    #     return render(request, 'user.html', {'data': property_data})


def hire_support(request):

    info = sessionInfo()
    if '0000' in info[0]:
        messages.warning(request, "Login to continue")
        return redirect('login')

    login_info = info[1]
    user = info[0]

    support = request.POST['support_id']
    property = request.POST['property_id']

    print(user, support, property)
    hired_retrieve = "select property_id_id, support_id_id from website_hires where user_id_id=%s"
    hired_data = None
    insert_into_hires = "insert into website_hires (property_id_id, user_id_id, support_id_id) values (%s,%s,%s)"
    insert_into_maintains = "insert into website_maintains (property_id_id,support_id_id) values (%s,%s)"
    with connection.cursor() as cursor:
        cursor.execute(hired_retrieve, [user])
        hired_data = tuple(cursor.fetchall())
        if (property, support,) in hired_data:
            messages.warning(request, 'Cannot add property')
        else:
            cursor.execute(insert_into_hires, (property, user, support))
            cursor.execute(insert_into_maintains, (property, support))
            messages.success(request, 'Added successfully!')

    return redirect('support')


def remove_support(request):
    info = sessionInfo()
    if '0000' in info[0]:
        messages.warning(request, "Login to continue")
        return redirect('login')

    info = sessionInfo()
    login_info = info[1]
    user = info[0]

    if request.method == 'POST':
        support = request.POST['support_id']
        property = request.POST['property_id']
        insert_pass = request.POST['confirm_password']
        retrieve_pass = 'select password from website_user where user_id=%s'
        hired_retrieve = "select property_id_id, support_id_id from website_hires where user_id_id=%s"
        hired_data = None

        psw = ''
        remove_from_hires = "delete from website_hires where property_id_id=%s and support_id_id=%s"
        remove_from_maintains = "delete from website_maintains where property_id_id=%s and support_id_id=%s"

        with connection.cursor() as cursor:
            cursor.execute(retrieve_pass, [info[0]])
            psw = tuple(cursor.fetchall())[0][0]
            if insert_pass == psw:
                cursor.execute(hired_retrieve, [user])
                hired_data = tuple(cursor.fetchall())
                if (property, support,) in hired_data:
                    # cursor.execute(add_auction_to_user, [info[0]])
                    cursor.execute(remove_from_hires, (property, support))
                    cursor.execute(remove_from_maintains, (property, support))
                    messages.success(request, 'Succesfully Removed Support')
                else:
                    messages.warning(request, "Property Not Added")
            else:
                messages.warning(request, 'Incorrect Password')

        return redirect('dashboard')


def user_edit_profile(request):
    info = sessionInfo()
    login_info = info[1]
    user = info[0]
    if 'user' in user:

        if request.method == 'POST':

            retrieve_user_info = "select username, address, email, password,user_img from website_user where user_id = %s"
            user_data = None
            image = ''
            with connection.cursor() as cursor:
                cursor.execute(retrieve_user_info, [user])
                user_data = tuple(cursor.fetchall())[0]
            old_dict = {
                'username': user_data[0],
                'address': user_data[1],
                'email': user_data[2],
                'password': user_data[3],
                'user_img': user_data[4]
            }
            if 'user_image' in request.FILES:
                image = request.FILES['user_image']
                with open("media/" + image.name, 'wb') as f:

                    for chunk in image.chunks():
                        f.write(chunk)
            else:
                image = ()
            password_changed = ''

            if 'current_password' in request.POST:
                current_pass = request.POST['current_password']
                if old_dict['password'] == current_pass:
                    if 'new_password' in request.POST and 'confirm_password' in request.POST:
                        new_pass = request.POST['new_password']
                        confirm_pass = request.POST['confirm_password']
                        if new_pass == confirm_pass:
                            password_changed = new_pass
                        else:
                            password_changed = 0
                            messages.warning(
                                request, 'Please retype new passwords properly')
                            return redirect('user_edit_profile')

            new_dict = {
                'username': request.POST['username'],
                'address': request.POST['address'],
                'email': request.POST['email'],
                'password': password_changed,
                'user_img': image.name if image != () else image
            }
            dict = {}
            flag = False
            for keys in new_dict.keys():
                if len(new_dict[keys]) != 0:
                    dict[keys] = new_dict[keys]
                    flag = True
                else:
                    dict[keys] = old_dict[keys]
            # print(dict,old_dict,new_dict)

            update_user = 'update website_user set username = %s, email= %s,address = %s,password =%s, user_img=%s where user_id = %s '
            with connection.cursor() as cursor:
                cursor.execute(update_user, (dict['username'], dict['email'],
                               dict['address'], dict['password'], dict['user_img'], user))
                if flag:
                    messages.success(request, "Profile Updated")
                else:
                    messages.info(request, 'Nothing to change in profile')
            return redirect('dashboard')

        return render(request, 'user_edit_profile.html', {'user_id': user})

    elif 'agent' in user:
        if request.method == 'POST':

            retrieve_agent_info = "select name, email, address,password, phone, agent_img from website_employee, website_agent where agent_id_id=employee_id and employee_id= %s"
            agent_data = None
            with connection.cursor() as cursor:
                cursor.execute(retrieve_agent_info, [user])
                agent_data = tuple(cursor.fetchall())[0]
            old_dict = {
                'agentname': agent_data[0],
                'email': agent_data[1],
                'address': agent_data[2],
                'password': agent_data[3],
                'phone': agent_data[4],
                'agent_img': agent_data[5]
            }
            if 'agent_image' in request.FILES:
                image = request.FILES['agent_image']
                with open("media/" + image.name, 'wb') as f:

                    for chunk in image.chunks():
                        f.write(chunk)
            else:
                image = ()
            password_changed = ''

            if 'current_password' in request.POST:
                current_pass = request.POST['current_password']
                if old_dict['password'] == current_pass:
                    if 'new_password' in request.POST and 'confirm_password' in request.POST:
                        new_pass = request.POST['new_password']
                        confirm_pass = request.POST['confirm_password']
                        if new_pass == confirm_pass:
                            password_changed = new_pass
                        else:
                            password_changed = 0
                            messages.warning(
                                request, 'Please retype new passwords properly')
                            return redirect('user_edit_profile')

            new_dict = {
                'agentname': request.POST['agentname'],
                'email': request.POST['email'],
                'address': request.POST['address'],
                'password': password_changed,
                'phone': request.POST['phone'],
                'agent_img': image.name if image != () else image
            }
            flag = False
            dict = {}
            for keys in new_dict.keys():
                if len(new_dict[keys]) != 0:
                    dict[keys] = new_dict[keys]
                    falg = True
                else:
                    dict[keys] = old_dict[keys]
            # print(dict,old_dict,new_dict)

            # update_user = 'update website_user set agentname = %s, email= %s,address = %s,password =%s, user_img=%s where user_id = %s '
            update_agent = 'UPDATE website_employee AS emp JOIN website_agent AS agent ON emp.employee_id = agent.agent_id_id SET emp.name = %s, emp.email = %s, emp.address = %s, emp.password = %s, emp.phone = %s, agent.agent_img = %s WHERE emp.employee_id = %s'
            with connection.cursor() as cursor:
                cursor.execute(update_agent, (dict['agentname'], dict['email'],
                               dict['address'], dict['password'], dict['phone'], dict['agent_img'], user))
                if flag:
                    messages.success(request, "Profile Updated")
                else:
                    messages.info(request, 'Nothing to change in profile')
            return redirect('dashboard')

        return render(request, 'agent_edit_profile.html', {'user_id': user})

    elif 'adm' in user:
        if request.method == 'POST':

            retrieve_admin_info = "select name, email, password from website_admin where admin_id = %s"
            admin_data = None
            with connection.cursor() as cursor:
                cursor.execute(retrieve_admin_info, [user])
                admin_data = tuple(cursor.fetchall())[0]
            old_dict = {
                'adminname': admin_data[0],
                'email': admin_data[1],
                'password': admin_data[2],
                # 'address' : admin_data[2],
                # 'phone' : admin_data[4],
                # 'agent_img': admin_data[5]
            }
            # image  = request.FILES['admin_image']
            # with open("media/" + image.name, 'wb') as f:

            #     for chunk in image.chunks():
            #         f.write(chunk)

            new_dict = {
                'adminname': request.POST['adminname'],
                'email': request.POST['email'],
                'password': request.POST['password'],
                # 'address' : request.POST['address'],
                # 'phone' : request.POST['phone'],
                # 'admin_img':image.name
            }
            dict = {}
            for keys in new_dict.keys():
                if len(new_dict[keys]) != 0:
                    dict[keys] = new_dict[keys]
                else:
                    dict[keys] = old_dict[keys]
            # print(dict,old_dict,new_dict)

            # update_user = 'update website_user set agentname = %s, email= %s,address = %s,password =%s, user_img=%s where user_id = %s '
            update_admin = 'UPDATE website_admin SET name = %s, email = %s, password = %s where admin_id = %s'
            with connection.cursor() as cursor:
                cursor.execute(
                    update_admin, (dict['adminname'], dict['email'], dict['password'], user))
                messages.success(request, "Profile Updated")
            return redirect('dashboard')

        return render(request, 'admin_edit_profile.html', {'user_id': user})


def property_edit_info(request):
    info = sessionInfo()
    login_info = info[1]
    user = info[0]

    if request.method == 'POST':
        property_id = request.POST['property_id']

        # print(property_id)
        retrieve_property_info = "select name,location,size,type,price,property_img from website_property where property_id = %s"
        property_data = None
        with connection.cursor() as cursor:
            cursor.execute(retrieve_property_info, [property_id])
            property_data = tuple(cursor.fetchall())[0]
        # print(property_data)
        old_dict = {
            'p_name': property_data[0],

            'location': property_data[1],
            'size': property_data[2],
            'type': property_data[3],
            'price': property_data[4],
            'property_img': property_data[5]
        }
        image = request.FILES['property_image']
        if image:
            with open("media/" + image.name, 'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)
        print(old_dict)
        new_dict = {
            'p_name': request.POST['p_name'],
            'location': request.POST['location'],
            'size': request.POST['size'],
            'type': request.POST['type'],
            'price': request.POST['price'],
            'property_img': image.name
        }
        # print(new_dict)
        dict = {}
        for keys in new_dict.keys():
            if len(new_dict[keys]) != 0:
                dict[keys] = new_dict[keys]
            else:
                dict[keys] = old_dict[keys]
        # print(dict,old_dict,new_dict)
        update_property = 'update website_property set name =%s,location=%s,size=%s,type=%s,price=%s,property_img = %s where property_id = %s '
        with connection.cursor() as cursor:
            cursor.execute(update_property, (dict['p_name'], dict['location'], dict['size'],
                           dict['type'], dict['price'], dict['property_img'], property_id))
            messages.success(request, "Property Info Updated")

    return render(request, 'property_edit_info.html', {'user_id': user, })


def auction(request):
    info = sessionInfo()
    login_info = info[1]
    user = info[0]
    if info[1] == "True":
        auction_id = ''
        property_data = ''
        user_status = ''
        auction_running_status = ''
        count_prop = ''
        all_auction = ''
        current_running = ''
        property_count = "select count(*) from website_auction_property where auction_id_id=%s"

        find_user_status = 'select auction_status from website_user where user_id=%s'
        find_auction = "select auction_id, auction_status, auction_running, auction_ended, start_time, total_properties from website_auction where auction_status='active'"
        find_property = """ 
                        select p.property_id, p.location, p.name, p.size, p.type, ap.starting_price, ap.increment, ap.selling_price, ap.number_of_bids, ap.owner_id_id
                        from website_auction as a
                        inner join website_auction_property as ap on a.auction_id = ap.auction_id_id
                        inner join website_property as p on ap.property_id_id = p.property_id
                        where a.auction_status = 'active' 
                        """
        if 'user' in info[0]:
            print('user is user')
            with connection.cursor() as cursor:
                cursor.execute(find_auction)
                temp = tuple(cursor.fetchall())
                print(temp, '----------')
                if len(temp) > 0:
                    auction_id = temp[0][0]
                    auction_running_status = temp[0][2]
                    current_running = temp[0]
                else:
                    auction_id = 0
                    auction_running_status = 0
                    current_running = 0
                print(auction_running_status, '---------------------')
                cursor.execute(find_property)
                property_data = tuple(cursor.fetchall())
                cursor.execute(find_user_status, [info[0]])
                user_status = tuple(cursor.fetchall())[0][0]
                dic = {
                    'user_id': info[0],
                    'auct_id': auction_id,
                    'data': property_data,
                    'user_status': user_status,
                    'running_status': auction_running_status,
                    'current_running': current_running
                }
                print(dic)
            return render(request, 'auction.html', dic)
        elif 'adm' in info[0]:
            find_all_auction = 'select auction_id, auction_status, auction_running, auction_ended, start_time, total_properties from website_auction'

            with connection.cursor() as cursor:
                cursor.execute(find_auction)
                temp = tuple(cursor.fetchall())

                print(temp)
                if len(temp) > 0:
                    auction_id = temp[0][0]
                    auction_running_status = temp[0][2]
                    current_running = temp[0]
                else:
                    auction_id = 0
                    auction_running_status = 0
                    current_running = 0
                cursor.execute(find_all_auction)
                all_auction = tuple(cursor.fetchall())
                if len(all_auction) < 1:
                    all_auction = 0
                cursor.execute(property_count, [auction_id])
                count_prop = tuple(cursor.fetchall())[0][0]
                print(auction_running_status, '---------------------')
                cursor.execute(find_property)
                property_data = tuple(cursor.fetchall())
                current_date = datetime.now().date()
                # current_date = current_date+timedelta(days=1)
            dic = {
                'user_id': info[0],
                'auct_id': auction_id,
                'data': property_data,
                'running_status': auction_running_status,
                'prop_count': count_prop,
                'all_auction': all_auction,
                'current_running': current_running,
                'current_date': current_date
            }
            print(dic, 'admin-dic')
            return render(request, 'auction.html', dic)
    else:
        prop_list = 0
        current_auction = 0
        find_auction = "select auction_id, auction_status, auction_running, auction_ended, start_time, total_properties from website_auction where auction_status='active'"
        find_property = """ 
                        select p.property_id, p.location, p.name, p.size, p.type, ap.starting_price
                        from website_auction as a
                        inner join website_auction_property as ap on a.auction_id = ap.auction_id_id
                        inner join website_property as p on ap.property_id_id = p.property_id
                        where a.auction_status = 'active' 
                        """
        with connection.cursor() as c:
            c.execute(find_auction)
            current_auction = tuple(c.fetchall())
            if len(current_auction) == 0:
                current_auction = 0
            else:
                current_auction = current_auction[0]
            c.execute(find_property)
            prop_list = tuple(c.fetchall())
            if len(prop_list) == 0:
                prop_list = 0
            else:
                prop_list = prop_list
            dic = {
                'data': prop_list,
                'current_auction': current_auction
            }
        return render(request, 'auction.html', dic)


def join_auction(request):
    info = sessionInfo()
    login_info = info[1]
    user = info[0]
    if info[1] == "True":
        if request.method == 'POST':
            insert_pass = request.POST['confirm_password']
            retrieve_pass = 'select password from website_user where user_id=%s'
            add_auction_to_user = "update website_user set auction_status='joined' where user_id=%s"
            psw = ''
            with connection.cursor() as cursor:
                cursor.execute(retrieve_pass, [info[0]])
                psw = tuple(cursor.fetchall())[0][0]
                if insert_pass == psw:
                    cursor.execute(add_auction_to_user, [info[0]])
                    messages.success(request, 'Succesfully joined Auction')
                else:
                    messages.warning(request, 'Incorrect Password')
    return redirect('auction')


def leave_auction(request):
    info = sessionInfo()
    login_info = info[1]
    user = info[0]
    if info[1] == "True":
        if request.method == 'POST':
            auction_id = request.POST['auct_id']
            print(auction_id)
            insert_pass = request.POST['confirm_password']
            retrieve_pass = 'select password from website_user where user_id=%s'
            user_prop_count = "select count(*) from website_auction_property where owner_id_id = %s and auction_id_id=%s"
            update_auction_prop_count = "update website_auction set total_properties = total_properties-%s"
            remove_auction_from_user = "update website_user set auction_status='not_joined' where user_id=%s"
            remove_auction_property = "delete from website_auction_property where owner_id_id = %s"
            psw = ''
            prop_count = ''
            with connection.cursor() as cursor:
                cursor.execute(retrieve_pass, [info[0]])
                psw = tuple(cursor.fetchall())[0][0]
                if insert_pass == psw:
                    cursor.execute(user_prop_count, (info[0], auction_id))
                    prop_count = tuple(cursor.fetchall())[0][0]
                    cursor.execute(update_auction_prop_count, [prop_count])
                    cursor.execute(remove_auction_property, [info[0]])
                    cursor.execute(remove_auction_from_user, [info[0]])
                    messages.warning(request, 'Left Auction')
                else:
                    messages.warning(request, 'Incorrect Password')
    return redirect('auction')


def auction_property_submission(request):
    info = sessionInfo()
    login_info = info[1]
    user = info[0]
    if info[1] == "True":
        if request.method == 'POST':
            auct_id = request.POST['auc_id']
            property_list = ''
            find_property = 'select property_id, name from website_property where user_id_id=%s and property_id not in (select property_id_id from website_auction_property where auction_id_id = %s)'
            with connection.cursor() as cursor:
                cursor.execute(find_property, (info[0], auct_id))
                property_list = tuple(cursor.fetchall())
            print(property_list)
            dic = {
                'user_id': info[0],
                'auct_id': auct_id,
                'properties': property_list
            }
            return render(request, 'confirm_property.html', dic)
    else:
        return render(request, 'confirm_property.html')


def auction_property_removal(request):
    info = sessionInfo()
    login_info = info[1]
    user = info[0]
    if info[1] == "True":
        if request.method == 'POST':
            property_list = ''
            auct_id = request.POST['auc_id']
            find_property = 'select property_id_id from website_auction_property where owner_id_id=%s '
            with connection.cursor() as cursor:
                cursor.execute(find_property, [info[0]])
                property_list = tuple(cursor.fetchall())
            dic = {
                'user_id': info[0],
                'properties': property_list,
                'auc_id': auct_id
            }
            return render(request, 'remove_auction_property.html', dic)
    else:
        return render(request, 'remove_auction_property.html')


def add_auction_property(request):
    info = sessionInfo()
    if '0000' in info[0]:
        messages.warning(request, 'Login to countinue')
        return redirect('login')
    login_info = info[1]
    user = info[0]
    if info[1] == "True":
        if request.method == 'POST':
            insert_prop = request.POST['prop_id']
            insert_starting_price = float(request.POST['starting_price'])
            print(type(insert_starting_price))
            insert_pass = request.POST['confirm_password']
            auction_id = request.POST['auct_id']
            retrieve_pass = 'select password from website_user where user_id=%s'
            update_auction_property = "UPDATE website_auction SET total_properties = total_properties + 1 WHERE auction_id = %s"
            insert_property = 'insert into website_auction_property (auction_id_id, owner_id_id, property_id_id, starting_price,selling_price,number_of_bids,increment,bidder_id_id) values (%s, %s,%s,%s, %s, %s, %s,%s)'
            check_password = ''
            user = ''
            with connection.cursor() as cursor:
                cursor.execute(retrieve_pass, [info[0]])
                check_password = tuple(cursor.fetchall())[0][0]
                if insert_pass == check_password:
                    cursor.execute(
                        insert_property, (auction_id, info[0], insert_prop, insert_starting_price, insert_starting_price, 0, 0.25, 'user_0001'))
                    cursor.execute(update_auction_property, [auction_id])
                    messages.success(request, 'Property Added to Auction')
                else:
                    messages.warning(request, ' Incorrect Password ')
    return redirect('auction')


def remove_auction_property(request):
    info = sessionInfo()
    login_info = info[1]
    user = info[0]
    if info[1] == "True":
        if request.method == 'POST':
            delete_prop = request.POST['prop_id']
            insert_pass = request.POST['confirm_password']
            auction_id = request.POST['auct_id']
            retrieve_pass = 'select password from website_user where user_id=%s'
            update_user = "update website_user set auction_status='joined'"
            delete_property = 'delete from website_auction_property where property_id_id = %s'
            update_auction_property = "UPDATE website_auction SET total_properties = total_properties - 1 WHERE auction_id = %s"
            psw = ''
            user = ''
            with connection.cursor() as cursor:
                cursor.execute(retrieve_pass, [info[0]])
                psw = tuple(cursor.fetchall())[0][0]
                if insert_pass == psw:
                    cursor.execute(delete_property, [delete_prop])
                    cursor.execute(update_auction_property, [auction_id])
                    messages.warning(request, 'Property Removed from Auction')
                else:
                    messages.warning(request, 'Incorrect Password ')
    return redirect('auction')


def create_auction(request):
    info = sessionInfo()
    fetch_auction = 'select auction_id from website_auction'
    get_password = 'select password from website_admin where admin_id = %s'
    create_auction = 'insert into website_auction (auction_id, auction_status, auction_running, start_time,auction_ended,total_properties) values (%s, %s, %s, %s,%b,%b)'
    auct_id = ''
    auction_status = 'active'
    auction_running = False
    time = request.POST['auction_time']
    psswd = request.POST['confirm_password']
    get_pass = ''
    print(time, 'time bro time')
    with connection.cursor() as cursor:
        cursor.execute(get_password, [info[0]])
        get_pass = tuple(cursor.fetchall())[0][0]
        if get_pass == psswd:
            cursor.execute(fetch_auction)
            temp = tuple(cursor.fetchall())
            entries = len(temp)
            auct_id = createAuct(entries+1)
            cursor.execute(
                create_auction, (auct_id, auction_status, auction_running, time, 0, 0))
            messages.success(request, "Auction created")
        else:
            messages.warning(request, "Password not correct")
    print(time)
    return redirect('auction')


def cancel_auction(request):
    info = sessionInfo()
    get_password = 'select password from website_admin where admin_id = %s'
    remove_auction = 'delete from website_auction where auction_id=%s'
    remove_property = 'delete from website_auction_property where auction_id_id=%s'
    auct_id = request.POST['auc_id']
    psswd = request.POST['confirm_password']
    get_pass = ''
    with connection.cursor() as cursor:
        cursor.execute(get_password, [info[0]])
        get_pass = tuple(cursor.fetchall())[0][0]
        if get_pass == psswd:
            cursor.execute(remove_property, [auct_id])
            cursor.execute(remove_auction, [auct_id])

            messages.success(request, "Auction Removed from database")
        else:
            messages.warning(request, "Password not correct")
    return redirect('auction')


def start_auction(request):
    if request.method == "POST":
        auct_id = request.POST['auc_id']
        set_running = 'update website_auction set auction_running = 1 where auction_id = %s'
        with connection.cursor() as c:
            c.execute(set_running, [auct_id])
            messages.success(request, f"Auction {auct_id} has started!")
    return redirect('auction')


def end_auction(request):
    if request.method == "POST":
        auct_id = request.POST['auc_id']
        set_ended = "update website_auction set auction_running = 0, auction_status='inacive', auction_ended=1 where auction_id = %s"
        set_ownership = 'update website_auction_property set owner_id_id = bidder_id_id where auction_id_id = %s'
        set_property = '''
            UPDATE website_property AS wp
            JOIN website_auction_property AS wap ON wp.property_id = wap.property_id_id
            SET 
                wp.price = wap.selling_price,
                wp.user_id_id = wap.owner_id_id,
                wp.status = 'sold' 
                WHERE wap.auction_id_id = %s
         '''
        # update user_id_id, price and status in website_property from website_auction_property
        with connection.cursor() as c:
            c.execute(set_ended, [auct_id])
            c.execute(set_ownership, [auct_id])
            c.execute(set_property, [auct_id])
            messages.success(request, f"Auction {auct_id} has Ended.")
    return redirect('auction')


def bid(request):
    info = sessionInfo()
    if request.method == "POST":
        prop_id = request.POST['auction_prop']
        set_bid = '''update website_auction_property 
                    set increment = increment+0.05, 
                    selling_price = selling_price+selling_price*increment, 
                    number_of_bids=number_of_bids+1,
                    bidder_id_id = %s where property_id_id = %s'''
        with connection.cursor() as c:
            c.execute(set_bid, (info[0], prop_id))
            messages.success(request, f"Bid to {prop_id} successful")
    return redirect('auction')


def agent_img(request):
    info = sessionInfo()
    login_info = info[1]
    if request.method == 'POST':
        image = request.FILES['agent_img']
        # print(image," image")
        with open('media/' + image.name, 'wb') as f:
            for chunk in image.chunks():
                f.write(chunk)
        insert = 'update website_agent set agent_img=%s where agent_id=%s'
        with connection.cursor() as cursor:
            cursor.execute(insert, (image.name, info[0]))
    if info[1] == "True":
        messages.success(request, 'Image uploaded successfully.')
        return redirect('user')
    else:
        return redirect('user')


def delete_from_market(request):
    info = sessionInfo()
    user = info[0]

    if request.method == "POST":
        password = request.POST['password']
        retrieve_password = 'select password from website_employee where employee_id = %s'
        confirm_password = ''
        with connection.cursor() as cursor:
            cursor.execute(retrieve_password, [user])
            confirm_password = tuple(cursor)[0][0]
        print("------------------------------", password, confirm_password)
        if password == confirm_password:

            property_id = request.POST['property_id']
            change_status = "update website_property set status = 'Available For Market' where property_id = %s"
            with connection.cursor() as cursor:
                cursor.execute(change_status, [property_id])
                messages.warning(request, 'Property Removed From Market')

        else:

            messages.warning(request, 'Incorrect Password')

    return redirect('dashboard')


def delete_property(request):
    info = sessionInfo()
    user = info[0]

    if request.method == "POST":
        property_id = request.POST['property_id']
        password = request.POST['password']
        retrieve_password = 'select password from website_user where user_id = %s'
        confirm_password = ''
        with connection.cursor() as cursor:
            cursor.execute(retrieve_password, [user])
            confirm_password = tuple(cursor)[0][0]
            cursor.execute(retrieve_hired, (user, property_id))
            check_hired = tuple(cursor.fetchall())

        print("ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
              confirm_password, password)
        print(check_hired, len(check_hired))
        if password == confirm_password:

            delete_property = 'delete from website_property where property_id = %s'
            with connection.cursor() as cursor:
                if len(check_hired) == 0:
                    cursor.execute(delete_property, [property_id])
                    messages.success(request, 'Property Removed Successfully')
                else:
                    messages.warning(request, 'Remove Support Before Deleting')
        else:
            messages.error(request, 'Incorrect Password')

    return redirect('dashboard')


# --------------------
# for every button function insert this code snippet at the very beginning to implement the default view

    # info = sessionInfo()
    # if '0000' in info[0]:
    #     return redirect('login')

# ----------------------

def countdown(request):
    pass
    return render(request, 'countdown.html')


def activity_support(request):
    info = sessionInfo()
    user = info[0]

    if request.method == "POST":
        support_retrieve = "select user_id_id, support_id_id from website_hires where user_id_id = %s"
        support_data = None
        with connection.cursor() as cursor:
            cursor.execute(support_retrieve, [user])
            support_data = tuple(cursor.fetchall())[0]
        if len(support_data) == 0:
            support_data = (user, 'No Supports Hired')
        return render(request, "user.html", {'user_data': user, 'support_data': support_data})
