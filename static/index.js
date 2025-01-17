
function add_document_form(){
    // Функция которая открывает меню поиска документов
    document.getElementById('main').innerHTML = document.getElementById('document_form_div').innerHTML;
}
function add_man_form(){
    // Функция которая открывает меню поиска людей
    document.getElementById('main').innerHTML = document.getElementById('man_form_div').innerHTML;
}

function add_additional_settings(){
    // Функция которая открывает или закрывает меню доп настроек поиска людей
    if(document.getElementById('additional_hidden').className == "d-none"){
        document.getElementById('additional_hidden').className = ""
    }
    else{
        document.getElementById('additional_hidden').className = "d-none"
    }
}

function send_request_man(){
    values = {}
    name = document.getElementById('names_input').value
    if(name!=""){
        values.name = name
    }
    chin = document.getElementById('chin_input').value
    if(chin!=""){
        values.chin = chin
    }
    rubric = document.getElementById('rubric_input').value
    if(rubric!=""){
        values.rubric = rubric
    }
    console.log(values)
    
    $.ajax(
        {
            url:  SCRIPT_ROOT+'/get_people',
            data: values,
            method: 'post',
            success: function(response){
                response = JSON.parse("[" + response + "]");
                console.log(response)
                if(response == 404){
                    document.getElementById('finded_thing').innerHTML = 'Не найдено'
                    document.getElementById('finded_thing').className = ""
                }
                else{
                    document.getElementById('finded_thing').className = "pt-4"
                    document.getElementById('finded_thing').innerHTML = ""
                    response[0].forEach(function(item, i, arr) {
                        document.getElementById('finded_thing').innerHTML += `<div class="row alert alert-dark" role="alert"><a href='${SCRIPT_ROOT}/people_info/${item[0]}'>${item[1]}</a></div>`   
                    });
                }

            },
            error: function(error){
                console.log(error)
            }
        }
    )
}

function send_request_document(){
    values = document.getElementById('document_name').value
    data = {}
    data.value = values
    $.ajax(
        {
            url:  SCRIPT_ROOT+'/get_document',
            data: data,
            method: 'post',
            success: function(response){
                console.log(response)
                if(response == 404){
                    document.getElementById('finded_thing').innerHTML = 'Не найдено'
                    document.getElementById('finded_thing').className = ""
                }
                else{
                    document.getElementById('finded_thing').className = "pt-4"
                    document.getElementById('finded_thing').innerHTML = ""
                    document.getElementById('finded_thing').innerHTML += `<div class="row alert alert-dark" role="alert"><a href='${SCRIPT_ROOT}/files/${response[1]}'>${response[0]}</a></div>`   

                }

            },
            error: function(error){
                console.log(error)
            }
        }
    )
}


function send_mail_follow(){
    values = document.getElementById('email_follow').value
    data = {}
    data.mail = values
    $.ajax(
        {
            url:  SCRIPT_ROOT+'/email_follow',
            data: data,
            method: 'post',
            success: function(response){
                console.log(response)
                if(response == 'error'){
                    alert('Данный email уже подписан на рассылку')
                }
                else{
                    alert('Успешно!')
                }

            },
            error: function(error){
                console.log(error)
            }
        }
    )
}
