import
client= {{ lookup('ini', 'client section=SAP file={{ config_file_path }}') }}
file= '/tmp/exp_qa_all.dat'