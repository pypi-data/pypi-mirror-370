from pathlib import Path
import subprocess
import os

base_dir = Path(__file__).parent
spass_output =  Path.cwd()  / "spass_output"
spass_output.mkdir(exist_ok=True)


default_config = {
    "problemName": "StepFrames",
    "name": "{*StepFrames*}",
    "author": "{*Author*}",
    "description":"{*Output of SPASS python file*}",
}


def load_config(config:dict[str,str] = default_config):
    problemName = config.get("problemName","StepFrames")
    name = config.get("name","Person")
    author = config.get("author","Author")
    description = config.get("description","Output of SPASS python file")

    if problemName.strip()=="":
        problemName = "StepFrames"

    if name.strip()=="":
        name = "Person"

    if author.strip()=="":
        author = "Author"

    if description.strip()=="":
        description = "Output of SPASS python file"

    return {"problemName":problemName,"name":name,"author":author,"description":description}


def create_dfg_file(config,first_order,S):
    dfg_code = f"""begin_problem({config["problemName"]}).

    list_of_descriptions.
    name({config["name"]}).
    author({config["author"]}).
    status(unsatisfiable).
    description({config["description"]}).
    end_of_list.
    

    list_of_symbols.
        functions[(f,1)].
        predicates[(R,2),(S,2)].
    end_of_list.


    list_of_formulae(axioms).
        formula(forall([v], exists([w], equal(f(w), v))), 1).
        {first_order}
        {S}
    end_of_list.    


    list_of_formulae(conjectures).
    
    formula(forall([w,v],equiv(R(w,v),exists([w1],and(S(w,w1),equal(f(w1),v))))),4).
    formula(forall([w,v],equiv(S(w,v),exists([k],and(R(k,v),S(w,k))))),5).
    
    end_of_list.

    end_problem.
    """

    with open(spass_output/"spass.dfg", "w") as f:
        f.write(dfg_code)


def run_SPASS():
    if not os.path.exists(f"{Path.cwd()}/spass39/SPASS"):
        raise FileExistsError("SPASS executable doesnt exist")
    
    SPASS_result = subprocess.run([Path.cwd()/"spass39/SPASS", spass_output/"spass.dfg"], capture_output=True, text=True)
    # return SPASS_result.stdout,SPASS_result.stderr
    with open(spass_output/"output.txt","w") as f:
        f.write(SPASS_result.stdout)

    with open(spass_output/"error.txt","w") as f:
        f.write(SPASS_result.stderr)

