# Before running the playbooks, make sure to activate the correct virtual environment:

python3 -m venv assignment3_env

# Activate the virtual environment

source assignment3_env/bin/activate

# Install the required packages (MUST BE IN THE VIRTUAL ENVIRONMENT)

pip install ansible openstacksdk python-openstackclient

# source the OpenStack RC file

source CH-822922-openrc.sh
(my chameleon CLI password is kurt4979 i think)

# Deactivate the virtual environment when done working on project

deactivate

# Run the playbooks

ansible-playbook -i Inventory -e "@variables.yaml" playbook_master.yaml

ansible-playbook -i Inventory -e "@variables.yaml" playbook_retrieve_facts_vms.yaml

ansible-playbook -i Inventory -e "@variables.yaml" playbook_step_by_step.yaml

# Add worker to the cluster
sudo kubeadm join 192.168.5.157:6443 --token 0t1es1.kwzvmgabudp2mvgz --discovery-token-ca-cert-hash sha256:4ac6635d6049e0b96f8825adaa255cf76d836d091cbc241e128f543b48a4b19c
