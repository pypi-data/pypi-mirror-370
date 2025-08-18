#!/bin/bash

# =============================================================================
# HELPER ACTIONS
# =============================================================================

NC=$(echo "\033[m")
BOLD=$(echo "\033[1;39m")
CMD=$(echo "\033[1;34m")
OPT=$(echo "\033[0;34m")

action_usage(){
    echo -e "    ____              __ _       __                "
    echo -e "   / __ )____  ____  / /| |     / /________ _____  "
    echo -e "  / __  / __ \/ __ \/ __/ | /| / / ___/ __ '/ __ \ "
    echo -e " / /_/ / /_/ / /_/ / /_ | |/ |/ / /  / /_/ / /_/ / "
    echo -e "/_____/\____/\____/\__/ |__/|__/_/   \__,_/ .___/  "
    echo -e "Python + Bootstrap                       /_/       " 
    echo -e ""                                          
    echo -e "${BOLD}System Commands:${NC}"
    echo -e "   ${CMD}init${NC} initializers environment;"
    echo -e "   ${CMD}test${OPT} ...${NC} runs tests;"
    echo -e "      ${OPT}-m <MARK> ${NC}runs tests for mark;"
    echo -e "      ${OPT}-c ${NC}generates code coverage summary;"
    echo -e "      ${OPT}-r ${NC}generates code coverage report;"
    echo -e "   ${CMD}preview${NC} runs web-server with documentation preview;"
    echo -e "   ${CMD}docs${NC} generates documentation (HTML-pages);"
    echo -e "   ${CMD}demo${NC} runs web-server with showcase project;" 
    echo -e "   ${CMD}build${NC} generates distribution archives;"  
}

action_init(){
    if [ -d .venv ];
        then
            rm -r .venv
    fi

    python3 -m venv .venv
    source .venv/bin/activate
    pip3 install -r requirements.txt
}

action_test(){
    source .venv/bin/activate

    OPTS=()
    while getopts ":m:cr" opt; do
        case $opt in
            m)
                OPTS+=(-m $OPTARG) 
                ;;
            c)
                OPTS+=(--cov=bootwrap) 
                ;;
            r)
                OPTS+=(--cov-report=xml:cov.xml) 
                ;;
            \?)
                echo -e "Invalid option: -$OPTARG"
                exit
                ;;
        esac
    done
    
    pytest --capture=no -p no:warnings ${OPTS[@]}
}

action_preview(){
    source .venv/bin/activate
    python main.py preview
}

action_docs(){
    source .venv/bin/activate
    python main.py docs
}

action_demo(){
    source .venv/bin/activate
    python main.py demo
}

action_build(){
    source .venv/bin/activate
    python -m build
}

# =============================================================================
# HELPER COMMANDS SELECTOR
# =============================================================================
case $1 in
    init)
        action_init
    ;;
    test)
        action_test ${@:2}
    ;;
    preview)
        action_preview
    ;;
    docs)
        action_docs
    ;;
    demo)
        action_demo
    ;;
    build)
        action_build
    ;;
    *)
        action_usage
    ;;
esac  

exit 0