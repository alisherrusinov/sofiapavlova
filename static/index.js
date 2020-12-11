
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
                document.getElementById('finded_thing').innerHTML = `<a href='${SCRIPT_ROOT}/people_info/${response[0][0]}'>${response[0][1]}</a>`
                document.getElementById('finded_thing').className = ""
            },
            error: function(error){
                console.log(error)
            }
        }
    )
}

function send_request_document(){
    value = document.getElementById('document_name').value
    data = {name:value}
    $.ajax(
        {
            url:  SCRIPT_ROOT+'/get_document',
            data: data,
            method: 'post',
            success: function(response){
                console.log(response)
            },
            error: function(error){
                console.log(error)
            }
        }
    )
}
