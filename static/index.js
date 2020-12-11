
function add_document_form(){
    document.getElementById('main').innerHTML = document.getElementById('document_form_div').innerHTML;
}
function add_man_form(){
    document.getElementById('main').innerHTML = document.getElementById('man_form_div').innerHTML;
}

function add_additional_settings(){
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
    year = document.getElementById('year_input').value
    if(year!=""){
        values.year = year
    }
    number = document.getElementById('number_input').value
    if(number!=""){
        values.number = number
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
                console.log(response)
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
