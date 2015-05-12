#include <sstream>
#include "python2.6/Python.h"
#include "maskstream.hpp"
#include "voidstream.hpp"
#include "parser_operations.hpp"
#include "libparser.hpp"
#include "client.hpp"

#ifdef PRECODE
#include PRECODE
#endif

extern "C" {

static PyObject* numerrin_version(PyObject *self, PyObject *args)
{
  string vstring=string("gcc version ")+__VERSION__+" build at "+__DATE__;
  return Py_BuildValue("s",vstring.c_str());
}

static PyObject* numerrin_initlocal(PyObject *self, PyObject *args)
{
  const char *cfile, *cenvvar, *ckey;
  if (!PyArg_ParseTuple(args,"sss",&cfile,&cenvvar,&ckey)) {
    PyErr_SetString(PyExc_RuntimeError,"Invalid arguments");
    return NULL;
  }
  string file(cfile), envvar(cenvvar), key(ckey);
  table<string> features;
  try {
    initialize_numerrin_local(file,envvar,key,features);
    if (features.getsize() == 0) {
      return Py_BuildValue("");
    }
    else {
      PyObject *feat=PyTuple_New(features.getsize());
      for (int i=0; i < features.getsize(); ++ i) {
        if (PyTuple_SetItem(feat,i,Py_BuildValue("s",features(i).c_str()))) {
          PyErr_SetString(PyExc_RuntimeError,"PyTuple_SetItem failed");
          return NULL;
        }
      }
      return feat;
    }
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError,e.what());
    return NULL;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError,"Unknown exception");
    return NULL;
  }
}

static PyObject* numerrin_initnetwork(PyObject *self, PyObject *args)
{
  int port;
  const char *caddr;
  if (!PyArg_ParseTuple(args,"si",&caddr,&port)) {
    PyErr_SetString(PyExc_RuntimeError,"Invalid arguments");
    return NULL;
  }
  string addr(caddr);
  try {
    Numerrin::client_instance::setkeys("30820275020100300D06092A864886F70D01010105000482025F3082025B02010002818100CEFD58F619A0E434C49D79D8269DF4492D4B5E55DDD3820613EC67B8825237659D15AA48443270BCEA8661E96C2B009C2577F7731B77B73B540162A653385E20329E5766D027AD13402F41E07046A704FE81020F8C05118870A864859E9AEA292AD9EE5E86004A2E29C8A49AF1825CC290D0A8206CB899934D196F408565671B020111028180027AF2D800DD65741551A498E63FCD1B172187D2BCA99367CFB7427F6C16BC9EC70A93E34E579C66A7E64801671526C513F83C2201B9353A6FB782DAF39C8FE861B65A415052894611261E2997C334E773985578CA62E27E03203A7C4C9061A351DB062A1F040C39DE3AFAEF5F2B1F96FABB53AAFC41D41CE09A3AFD7BD3602D024100E299497ACC45C98F22E07B00154703BBC4035AE08C1CA61F69EE3283B0FC37DBB236A9CE49CB049B87FE09A1914728343E9AFBD5289BF5BB0F49BCD016E9F905024100E9D8B8FE603FAF09CBF8F1AE5616EFD58B8EE17162F1DB6C01DB7E36C97623C9E0B1138F3712036F75792A65142C5C9C386A3747F0D57E113442A5FC9C4D599F024100BA9C5AA15CEE2D84EF8BB096A81C5D6D743EFF8BBEAE2E74391E83F3FB2A0FE21A4B226DA62EB88015A407EE77A402FDD93456EBC717069A0C9713F6A97563A9024044C74577FE30D920FFC1B07E91CA82C6563915215956317A1EA9F7F1FF04A11D4215F6B1A6C91011B923A30EAB9493B57A011F5164F37F6E78C84EEFF1BC65A7024100B304F62040FD9603312BC487F0A38EEA3344DA953FA02B2AE241F189CBE8FCB66523C999C21A0CD3051A3635E441A90DB2DFA3B13763825B65D7138E574A8B7E","30819D300D06092A864886F70D010101050003818B0030818702818100D961A437454B3DAAE09B02E8A13EF7E73D8F2BF82A538785784D88B5F8A8B23F77BCA54159E2EDFE19F3D10D3CE37FAE48A10EC0CB4D357359DD022D1DBDB029AD6237F1E8B1BFB2750B9A1F20008441EBAEFCD964D06EF0EF59F2999A8622D35D20E1D85F073C18241EE0B5926E243199C099D2A85668D7CAFAFAB2CADCFF6B020111");
    table<string> features;
    initialize_numerrin_floating(string("pynumerrin4"),addr,port,features);
    if (features.getsize() == 0) {
      return Py_BuildValue("");
    }
    else {
      PyObject *feat=PyTuple_New(features.getsize());
      for (int i=0; i < features.getsize(); ++ i) {
        if (PyTuple_SetItem(feat,i,Py_BuildValue("s",features(i).c_str()))) {
          PyErr_SetString(PyExc_RuntimeError,"PyTuple_SetItem failed");
          return NULL;
        }
      }
      return feat;
    }
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError,e.what());
    return NULL;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError,"Unknown exception");
    return NULL;
  }
}

static PyObject* numerrin_releasenetwork(PyObject *self, PyObject *args)
{
  int port;
  const char *caddr;
  if (!PyArg_ParseTuple(args,"si",&caddr,&port)) {
    PyErr_SetString(PyExc_RuntimeError,"Invalid arguments");
    return NULL;
  }
  string addr(caddr);
  try {
    release_license_floating(string("pynumerrin4"),addr,port);
    return Py_BuildValue("");
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError,e.what());
    return NULL;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError,"Unknown exception");
    return NULL;
  }
}

static PyObject* numerrin_createpool(PyObject *self, PyObject *args)
{
  try {
    int ph=create_pool();
    return Py_BuildValue("i",ph);
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError,e.what());
    return NULL;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError,"Unknown exception");
    return NULL;
  }
}

static PyObject* numerrin_deletepool(PyObject *self, PyObject *args)
{
  int ph;
  if (!PyArg_ParseTuple(args,"i",&ph)) {
    PyErr_SetString(PyExc_RuntimeError,"Invalid arguments");
    return NULL;
  }
  try {
    delete_pool(ph);
    return Py_BuildValue("");
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError,e.what());
    return NULL;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError,"Unknown exception");
    return NULL;
  }
}

static PyObject* numerrin_clearpool(PyObject *self, PyObject *args)
{
  int ph;
  if (!PyArg_ParseTuple(args,"i",&ph)) {
    PyErr_SetString(PyExc_RuntimeError,"Invalid arguments");
    return NULL;
  }
  try {
    clear_pool(ph);
    return Py_BuildValue("");
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError,e.what());
    return NULL;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError,"Unknown exception");
    return NULL;
  }
}

static PyObject* numerrin_createcode(PyObject *self, PyObject *args)
{
  try {
    int ch=create_code();
    return Py_BuildValue("i",ch);
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError,e.what());
    return NULL;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError,"Unknown exception");
    return NULL;
  }
}

static PyObject* numerrin_deletecode(PyObject *self, PyObject *args)
{
  int ch;
  if (!PyArg_ParseTuple(args,"i",&ch)) {
    PyErr_SetString(PyExc_RuntimeError,"Invalid arguments");
    return NULL;
  }
  try {
    delete_code(ch);
    return Py_BuildValue("");
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError,e.what());
    return NULL;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError,"Unknown exception");
    return NULL;
  }
}

static PyObject* numerrin_clearcode(PyObject *self, PyObject *args)
{
  int ch;
  if (!PyArg_ParseTuple(args,"i",&ch)) {
    PyErr_SetString(PyExc_RuntimeError,"Invalid arguments");
    return NULL;
  }
  try {
    clear_code(ch);
    return Py_BuildValue("");
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError,e.what());
    return NULL;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError,"Unknown exception");
    return NULL;
  }
}

static PyObject* numerrin_parsefile(PyObject *self, PyObject *args)
{
  int ph, ch;
  const char *fn;
  if (!PyArg_ParseTuple(args,"iis",&ph,&ch,&fn)) {
    PyErr_SetString(PyExc_RuntimeError,"Invalid arguments");
    return NULL;
  }
  try {
    ifstream srcs(fn);
    if (!srcs.good()) {
      string error("Can't open file ");
      error += fn;
      PyErr_SetString(PyExc_RuntimeError,error.c_str());
      return NULL;
    }
    parse_code(ph,ch,srcs);
    return Py_BuildValue("");
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError,e.what());
    return NULL;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError,"Unknown exception");
    return NULL;
  }
}

static PyObject* numerrin_parsestring(PyObject *self, PyObject *args)
{
  int ph, ch;
  char *src;
  if (!PyArg_ParseTuple(args,"iis",&ph,&ch,&src)) {
    PyErr_SetString(PyExc_RuntimeError,"Invalid arguments");
    return NULL;
  }
  try {
    std::istringstream srcs(src);
    parse_code(ph,ch,srcs);
    return Py_BuildValue("");
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError,e.what());
    return NULL;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError,"Unknown exception");
    return NULL;
  }
}

static PyObject* numerrin_execute(PyObject *self, PyObject *args)
{
  int ph, ch, nproc;
  if (!PyArg_ParseTuple(args,"iii",&ph,&ch,&nproc)) {
    PyErr_SetString(PyExc_RuntimeError,"Invalid arguments");
    return NULL;
  }
  try {
    maskstream ms(cout);
    execute_code(ph,ch,nproc,ms);
    return Py_BuildValue("");
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError,e.what());
    return NULL;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError,"Unknown exception");
    return NULL;
  }
}

static PyObject* numerrin_clearvariable(PyObject *self, PyObject *args)
{
  int ph;
  const char *chain;
  if (!PyArg_ParseTuple(args,"is",&ph,&chain)) {
    PyErr_SetString(PyExc_RuntimeError,"Invalid arguments");
    return NULL;
  }
  try {
    clear_variable(ph,chain);
    return Py_BuildValue("");
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError,e.what());
    return NULL;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError,"Unknown exception");
    return NULL;
  }
}

static PyObject* numerrin_gettype(PyObject *self, PyObject *args)
{
  int ph;
  const char *chain;
  if (!PyArg_ParseTuple(args,"is",&ph,&chain)) {
    PyErr_SetString(PyExc_RuntimeError,"Invalid arguments");
    return NULL;
  }
  try {
    int type=get_variable_type(ph,string(chain));
    return Py_BuildValue("s",typenames[type]);
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError,e.what());
    return NULL;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError,"Unknown exception");
    return NULL;
  }
}

static PyObject* numerrin_getrank(PyObject *self, PyObject *args)
{
  int ph;
  const char *chain;
  if (!PyArg_ParseTuple(args,"is",&ph,&chain)) {
    PyErr_SetString(PyExc_RuntimeError,"Invalid arguments");
    return NULL;
  }
  try {
    int rank=get_variable_rank(ph,string(chain));
    return Py_BuildValue("i",rank);
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError,e.what());
    return NULL;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError,"Unknown exception");
    return NULL;
  }
}

static PyObject* numerrin_getsize(PyObject *self, PyObject *args)
{
  int ph;
  const char *chain;
  if (!PyArg_ParseTuple(args,"is",&ph,&chain)) {
    PyErr_SetString(PyExc_RuntimeError,"Invalid arguments");
    return NULL;
  }
  try {
    vector<int> size;
    get_variable_size(ph,string(chain),size);
    PyObject *sizes=PyTuple_New(size.getsize());
    for (int i=0; i < size.getsize(); ++ i) {
      if (PyTuple_SetItem(sizes,i,Py_BuildValue("i",size(i)))) {
        PyErr_SetString(PyExc_RuntimeError,"PyTuple_SetItem failed");
        return NULL;
      }
    }
    return sizes;
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError,e.what());
    return NULL;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError,"Unknown exception");
    return NULL;
  }
}

PyObject* getvalue(int level, multi_index<long>& mi, parser_variable& var)
{
  if (level < 0) {
    switch (var.gettype()) {
    case BOOL_VAR:
      return Py_BuildValue("i",int(var.get_p_bool()(0L)));
    case INT_VAR:
      return Py_BuildValue("l",var.get_p_int()(0L));
    case REAL_VAR:
      return Py_BuildValue("d",var.get_p_real()(0L));
    case COMPLEX_VAR:
      Py_complex c;
      c.real=real(var.get_p_complex()(0L));
      c.imag=imag(var.get_p_complex()(0L));
      return PyComplex_FromCComplex(c);
    case STRING_VAR:
      return Py_BuildValue("s",var.get_p_string()(0L).c_str());
    default:
      PyErr_SetString(PyExc_RuntimeError,"Unsupported variable type");
      return NULL;
    }
  }
  if (level == 0) {
    Py_complex c;
    PyObject *ret=PyTuple_New(mi.getlim(0));
    for (mi.begin(0); mi.inrange(0); mi.inconlyrank(0)) {
      switch (var.gettype()) {
      case BOOL_VAR:
        if (PyTuple_SetItem(ret,mi.geti(0L),Py_BuildValue("i",int(var.get_p_bool()(mi))))) {
          PyErr_SetString(PyExc_RuntimeError,"PyTuple_SetItem failed");
          return NULL;
        }
        break;
      case INT_VAR:
        if (PyTuple_SetItem(ret,mi.geti(0L),Py_BuildValue("l",var.get_p_int()(mi)))) {
          PyErr_SetString(PyExc_RuntimeError,"PyTuple_SetItem failed");
          return NULL;
        }
        break;
      case REAL_VAR:
        if (PyTuple_SetItem(ret,mi.geti(0L),Py_BuildValue("d",var.get_p_real()(mi)))) {
          PyErr_SetString(PyExc_RuntimeError,"PyTuple_SetItem failed");
          return NULL;
        }
        break;
      case COMPLEX_VAR:
        c.real=real(var.get_p_complex()(mi));
        c.imag=imag(var.get_p_complex()(mi));
        if (PyTuple_SetItem(ret,mi.geti(0L),PyComplex_FromCComplex(c))) {
          PyErr_SetString(PyExc_RuntimeError,"PyTuple_SetItem failed");
          return NULL;
        }
        break;
      case STRING_VAR:
        if (PyTuple_SetItem(ret,mi.geti(0L),Py_BuildValue("s",var.get_p_string()(mi).c_str()))) {
          PyErr_SetString(PyExc_RuntimeError,"PyTuple_SetItem failed");
          return NULL;
        }
        break;
      default:
        PyErr_SetString(PyExc_RuntimeError,"Unsupported variable type");
        return NULL;
      }
    }
    return ret;
  }
  else {
    PyObject *ret=PyTuple_New(mi.getlim(level));
    for (mi.begin(level); mi.inrange(level); mi.inconlyrank(level)) {
      if (PyTuple_SetItem(ret,mi.geti(level),getvalue(level-1,mi,var))) {
        PyErr_SetString(PyExc_RuntimeError,"PyTuple_SetItem failed");
        return NULL;
      }
    }
    return ret;
  }
}

static PyObject* numerrin_getvariable(PyObject *self, PyObject *args)
{
  int ph;
  const char *chain;
  if (!PyArg_ParseTuple(args,"is",&ph,&chain)) {
    PyErr_SetString(PyExc_RuntimeError,"Invalid arguments");
    return NULL;
  }
  try {
    parser_variable v;
    get_variable(ph,string(chain),v);
    multi_index<long> mi(v.getrank(),v.getsize());
    return getvalue(v.getrank()-1,mi,v);
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError,e.what());
    return NULL;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError,"Unknown exception");
    return NULL;
  }
}

void putint(int level, multi_index<long>& mi, parser_variable& v, PyObject *po)
{
  if (level < 0) {
    v.get_p_int()(0L)=PyInt_AsLong(po);
    return;
  }
  if (level == 0) {
    for (mi.begin(0); mi.inrange(0); mi.inconlyrank(0)) {
      v.get_p_int()(mi)=PyInt_AsLong(PyTuple_GetItem(po,mi.geti(0)));
    }
  }
  else {
    for (mi.begin(level); mi.inrange(level); mi.inconlyrank(level)) {
      putint(level-1,mi,v,PyTuple_GetItem(po,mi.geti(level)));
    }
  }
}

void putlong(int level, multi_index<long>& mi, parser_variable& v, PyObject *po)
{
  if (level < 0) {
    v.get_p_int()(0L)=PyLong_AsLong(po);
    return;
  }
  if (level == 0) {
    for (mi.begin(0); mi.inrange(0); mi.inconlyrank(0)) {
      v.get_p_int()(mi)=PyLong_AsLong(PyTuple_GetItem(po,mi.geti(0)));
    }
  }
  else {
    for (mi.begin(level); mi.inrange(level); mi.inconlyrank(level)) {
      putlong(level-1,mi,v,PyTuple_GetItem(po,mi.geti(level)));
    }
  }
}

void putdouble(int level, multi_index<long>& mi, parser_variable& v, PyObject *po)
{
  if (level < 0) {
    v.get_p_real()(0L)=PyFloat_AsDouble(po);
    return;
  }
  if (level == 0) {
    for (mi.begin(0); mi.inrange(0); mi.inconlyrank(0)) {
      v.get_p_real()(mi)=PyFloat_AsDouble(PyTuple_GetItem(po,mi.geti(0)));
    }
  }
  else {
    for (mi.begin(level); mi.inrange(level); mi.inconlyrank(level)) {
      putdouble(level-1,mi,v,PyTuple_GetItem(po,mi.geti(level)));
    }
  }
}

void putcomplex(int level, multi_index<long>& mi, parser_variable& v, PyObject *po)
{
  if (level < 0) {
    Py_complex c;
    c=PyComplex_AsCComplex(po);
    v.get_p_complex()(0L)=complex<double>(c.real,c.imag);
    return;
  }
  if (level == 0) {
    Py_complex c;
    for (mi.begin(0); mi.inrange(0); mi.inconlyrank(0)) {
      c=PyComplex_AsCComplex(PyTuple_GetItem(po,mi.geti(0)));
      v.get_p_complex()(mi)=complex<double>(c.real,c.imag);
    }
  }
  else {
    for (mi.begin(level); mi.inrange(level); mi.inconlyrank(level)) {
      putdouble(level-1,mi,v,PyTuple_GetItem(po,mi.geti(level)));
    }
  }
}

void putstring(int level, multi_index<long>& mi, parser_variable& v, PyObject *po)
{
  if (level < 0) {
    v.get_p_string()(0L)=PyString_AsString(po);
    return;
  }
  if (level == 0) {
    for (mi.begin(0); mi.inrange(0); mi.inconlyrank(0)) {
      v.get_p_string()(mi)=PyString_AsString(PyTuple_GetItem(po,mi.geti(0)));
    }
  }
  else {
    for (mi.begin(level); mi.inrange(level); mi.inconlyrank(level)) {
      putstring(level-1,mi,v,PyTuple_GetItem(po,mi.geti(level)));
    }
  }
}

static PyObject* numerrin_putvariable(PyObject *self, PyObject *args)
{
  int ph;
  const char *chain;
  PyObject *po;
  if (!PyArg_ParseTuple(args,"isO",&ph,&chain,&po)) {
    PyErr_SetString(PyExc_RuntimeError,"Invalid arguments");
    return NULL;
  }
  try {
    PyObject *part=po;
    table<long> sizes;
    while (PyTuple_Check(part)) {
      sizes.add(PyTuple_Size(part));
      part=PyTuple_GetItem(part,0);
    }
    long tmp;
    for (int i=0; i < sizes.getsize() >> 1; ++ i) {
      tmp=sizes(i); sizes(i)=sizes(sizes.getsize()-1-i); sizes(sizes.getsize()-1-i)=tmp;
    }
    if (PyInt_Check(part)) {
      parser_variable v;
      v.init(INT_VAR,sizes.getsize(),sizes.ptr());
      multi_index<long> mi(v.getrank(),v.getsize());
      putint(v.getrank()-1,mi,v,po);
      put_variable(ph,chain,v);
      return Py_BuildValue("");
    }
    if (PyLong_Check(part)) {
      parser_variable v;
      v.init(INT_VAR,sizes.getsize(),sizes.ptr());
      multi_index<long> mi(v.getrank(),v.getsize());
      putlong(v.getrank()-1,mi,v,po);
      put_variable(ph,chain,v);
      return Py_BuildValue("");
    }
    if (PyFloat_Check(part)) {
      parser_variable v;
      v.init(REAL_VAR,sizes.getsize(),sizes.ptr());
      multi_index<long> mi(v.getrank(),v.getsize());
      putdouble(v.getrank()-1,mi,v,po);
      put_variable(ph,chain,v);
      return Py_BuildValue("");
    }
    if (PyComplex_Check(part)) {
      parser_variable v;
      v.init(COMPLEX_VAR,sizes.getsize(),sizes.ptr());
      multi_index<long> mi(v.getrank(),v.getsize());
      putcomplex(v.getrank()-1,mi,v,po);
      put_variable(ph,chain,v);
      return Py_BuildValue("");
    }
    if (PyString_Check(part)) {
      parser_variable v;
      v.init(STRING_VAR,sizes.getsize(),sizes.ptr());
      multi_index<long> mi(v.getrank(),v.getsize());
      putstring(v.getrank()-1,mi,v,po);
      put_variable(ph,chain,v);
      return Py_BuildValue("");
    }
    PyErr_SetString(PyExc_RuntimeError,"Unsupported variable type");
    return NULL;
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError,e.what());
    return NULL;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError,"Unknown exception");
    return NULL;
  }
}

static PyObject* numerrin_modifyvariable(PyObject *self, PyObject *args)
{
  int ph;
  const char *chain;
  PyObject *po;
  if (!PyArg_ParseTuple(args,"isO",&ph,&chain,&po)) {
    PyErr_SetString(PyExc_RuntimeError,"Invalid arguments");
    return NULL;
  }
  try {
    PyObject *part=po;
    table<long> sizes;
    while (PyTuple_Check(part)) {
      sizes.add(PyTuple_Size(part));
      part=PyTuple_GetItem(part,0);
    }
    long tmp;
    for (int i=0; i < sizes.getsize() >> 1; ++ i) {
      tmp=sizes(i); sizes(i)=sizes(sizes.getsize()-1-i); sizes(sizes.getsize()-1-i)=tmp;
    }
    if (PyInt_Check(part)) {
      parser_variable v;
      v.init(INT_VAR,sizes.getsize(),sizes.ptr());
      multi_index<long> mi(v.getrank(),v.getsize());
      putint(v.getrank()-1,mi,v,po);
      modify_variable(ph,chain,v);
      return Py_BuildValue("");
    }
    if (PyLong_Check(part)) {
      parser_variable v;
      v.init(INT_VAR,sizes.getsize(),sizes.ptr());
      multi_index<long> mi(v.getrank(),v.getsize());
      putlong(v.getrank()-1,mi,v,po);
      modify_variable(ph,chain,v);
      return Py_BuildValue("");
    }
    if (PyFloat_Check(part)) {
      parser_variable v;
      v.init(REAL_VAR,sizes.getsize(),sizes.ptr());
      multi_index<long> mi(v.getrank(),v.getsize());
      putdouble(v.getrank()-1,mi,v,po);
      modify_variable(ph,chain,v);
      return Py_BuildValue("");
    }
    if (PyComplex_Check(part)) {
      parser_variable v;
      v.init(COMPLEX_VAR,sizes.getsize(),sizes.ptr());
      multi_index<long> mi(v.getrank(),v.getsize());
      putcomplex(v.getrank()-1,mi,v,po);
      modify_variable(ph,chain,v);
      return Py_BuildValue("");
    }
    if (PyString_Check(part)) {
      parser_variable v;
      v.init(STRING_VAR,sizes.getsize(),sizes.ptr());
      multi_index<long> mi(v.getrank(),v.getsize());
      putstring(v.getrank()-1,mi,v,po);
      modify_variable(ph,chain,v);
      return Py_BuildValue("");
    }
    PyErr_SetString(PyExc_RuntimeError,"Unsupported variable type");
    return NULL;
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError,e.what());
    return NULL;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError,"Unknown exception");
    return NULL;
  }
}

static PyObject* numerrin_getrealfunction(PyObject *self, PyObject *args)
{
  int ph;
  const char *chain;
  if (!PyArg_ParseTuple(args,"is",&ph,&chain)) {
    PyErr_SetString(PyExc_RuntimeError,"Invalid arguments");
    return NULL;
  }
  try {
    num_long tsz, tst;
    parser_variable v;
    get_real_function(ph,string(chain),v.get_p_real());
    v.settype(REAL_VAR);
    tsz=v.get_p_real().getsize()[0];
    tst=v.get_p_real().getstep()[0];
    for (int i=1; i < v.getrank(); ++ i) {
      v.get_p_real().getsize()[i-1]=v.get_p_real().getsize()[i];
      v.get_p_real().getstep()[i-1]=v.get_p_real().getstep()[i];
    }
    v.get_p_real().getsize()[v.getrank()-1]=tsz;
    v.get_p_real().getstep()[v.getrank()-1]=tst;
    multi_index<long> mi(v.getrank(),v.getsize());
    return getvalue(v.getrank()-1,mi,v);
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError,e.what());
    return NULL;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError,"Unknown exception");
    return NULL;
  }
}

static PyObject* numerrin_initmesh(PyObject *self, PyObject *args)
{
  int ph, dim, nnodes;
  const char *chain;
  PyObject *po;
  if (!PyArg_ParseTuple(args,"isiO",&ph,&chain,&dim,&po)) {
    PyErr_SetString(PyExc_RuntimeError,"Invalid arguments");
    return NULL;
  }
  try {
    table<int> elenum;
    if (PyTuple_Check(po)) {
      if (PyInt_Check(PyTuple_GetItem(po,0))) {
        nnodes=int(PyInt_AsLong(PyTuple_GetItem(po,0)));
        for (int i=1; i < PyTuple_Size(po); ++ i) {
          elenum.add(int(PyInt_AsLong(PyTuple_GetItem(po,i))));
        }
        initialize_mesh(ph,chain,dim,nnodes,elenum);
        return Py_BuildValue("");
      }
      if (PyLong_Check(PyTuple_GetItem(po,0))) {
        nnodes=int(PyLong_AsLong(PyTuple_GetItem(po,0)));
        for (int i=1; i < PyTuple_Size(po); ++ i) {
          elenum.add(int(PyLong_AsLong(PyTuple_GetItem(po,i))));
        }
        initialize_mesh(ph,chain,dim,nnodes,elenum);
        return Py_BuildValue("");
      }
    }
    PyErr_SetString(PyExc_RuntimeError,"Integer sizes required");
    return NULL;
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError,e.what());
    return NULL;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError,"Unknown exception");
    return NULL;
  }
}

static PyObject* numerrin_setnode(PyObject *self, PyObject *args)
{
  int ph, nodenum;
  const char *chain;
  PyObject *po;
  if (!PyArg_ParseTuple(args,"isiO",&ph,&chain,&nodenum,&po)) {
    PyErr_SetString(PyExc_RuntimeError,"Invalid arguments");
    return NULL;
  }
  try {
    if (PyTuple_Check(po)) {
      if (PyFloat_Check(PyTuple_GetItem(po,0))) {
        vector<double> x(PyTuple_Size(po));
        for (int i=0; i < PyTuple_Size(po); ++ i) {
          x.put(i,PyFloat_AsDouble(PyTuple_GetItem(po,i)));
        }
        set_node(ph,chain,nodenum,x);
        return Py_BuildValue("");
      }
    }
    PyErr_SetString(PyExc_RuntimeError,"Double node coordinates required");
    return NULL;
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError,e.what());
    return NULL;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError,"Unknown exception");
    return NULL;
  }
}

static PyObject* numerrin_setelementtype(PyObject *self, PyObject *args)
{
  int ph, elvl, elnum, etype;
  const char *chain;
  if (!PyArg_ParseTuple(args,"isiii",&ph,&chain,&elvl,&elnum,&etype)) {
    PyErr_SetString(PyExc_RuntimeError,"Invalid arguments");
    return NULL;
  }
  try {
    set_elementtype(ph,chain,elvl,elnum,etype);
    return Py_BuildValue("");
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError,e.what());
    return NULL;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError,"Unknown exception");
    return NULL;
  }
}

static PyObject* numerrin_setelement(PyObject *self, PyObject *args)
{
  int ph, elvl, elnum, rlvl;
  const char *chain;
  PyObject *po;
  if (!PyArg_ParseTuple(args,"isiiiO",&ph,&chain,&elvl,&elnum,&rlvl,&po)) {
    PyErr_SetString(PyExc_RuntimeError,"Invalid arguments");
    return NULL;
  }
  try {
    table<int> ref;
    if (PyTuple_Check(po)) {
      if (PyInt_Check(PyTuple_GetItem(po,0))) {
        for (int i=0; i < PyTuple_Size(po); ++ i) {
          ref.add(int(PyInt_AsLong(PyTuple_GetItem(po,i))));
        }
        set_element(ph,chain,elvl,elnum,rlvl,ref);
        return Py_BuildValue("");
      }
      if (PyLong_Check(PyTuple_GetItem(po,0))) {
        for (int i=0; i < PyTuple_Size(po); ++ i) {
          ref.add(int(PyLong_AsLong(PyTuple_GetItem(po,i))));
        }
        set_element(ph,chain,elvl,elnum,rlvl,ref);
        return Py_BuildValue("");
      }
    }
    PyErr_SetString(PyExc_RuntimeError,"Integer sizes required");
    return NULL;
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError,e.what());
    return NULL;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError,"Unknown exception");
    return NULL;
  }
}

static PyObject* numerrin_meshsize(PyObject *self, PyObject *args)
{
  int ph;
  const char *chain;
  if (!PyArg_ParseTuple(args,"is",&ph,&chain)) {
    PyErr_SetString(PyExc_RuntimeError,"Invalid arguments");
    return NULL;
  }
  try {
    vector<int> sz;
    mesh_size(ph,chain,sz);
    PyObject *siz=PyTuple_New(sz.getsize());
    for (int i=0; i < sz.getsize(); ++ i) {
      if (PyTuple_SetItem(siz,i,Py_BuildValue("i",sz(i)))) {
        PyErr_SetString(PyExc_RuntimeError,"PyTuple_SetItem failed");
        return NULL;
      }
    }
    return siz;
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError,e.what());
    return NULL;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError,"Unknown exception");
    return NULL;
  }
}

static PyObject* numerrin_getnode(PyObject *self, PyObject *args)
{
  int ph, nnum;
  const char *chain;
  if (!PyArg_ParseTuple(args,"isi",&ph,&chain,&nnum)) {
    PyErr_SetString(PyExc_RuntimeError,"Invalid arguments");
    return NULL;
  }
  try {
    vector<double> v;
    get_node(ph,chain,nnum,v);
    PyObject *nc=PyTuple_New(v.getsize());
    for (int i=0; i < v.getsize(); ++ i) {
      if (PyTuple_SetItem(nc,i,Py_BuildValue("d",v(i)))) {
        PyErr_SetString(PyExc_RuntimeError,"PyTuple_SetItem failed");
        return NULL;
      }
    }
    return nc;
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError,e.what());
    return NULL;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError,"Unknown exception");
    return NULL;
  }
}

static PyObject* numerrin_getelement(PyObject *self, PyObject *args)
{
  int ph, elvl, elnum, rlvl;
  const char *chain;
  if (!PyArg_ParseTuple(args,"isiii",&ph,&chain,&elvl,&elnum,&rlvl)) {
    PyErr_SetString(PyExc_RuntimeError,"Invalid arguments");
    return NULL;
  }
  try {
    table<int> ref;
    get_element(ph,chain,elvl,elnum,rlvl,ref);
    PyObject *en=PyTuple_New(ref.getsize());
    for (int i=0; i < ref.getsize(); ++ i) {
      if (PyTuple_SetItem(en,i,Py_BuildValue("i",ref(i)))) {
        PyErr_SetString(PyExc_RuntimeError,"PyTuple_SetItem failed");
        return NULL;
      }
    }
    return en;
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError,e.what());
    return NULL;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError,"Unknown exception");
    return NULL;
  }
}

static PyMethodDef NumerrinMethods[] = {
  {"version",numerrin_version,METH_VARARGS,"Get the version (build) information."},
  {"initlocal",numerrin_initlocal,METH_VARARGS,"Initialize Numerrin with a local license."},
  {"initnetwork",numerrin_initnetwork,METH_VARARGS,"Initialize Numerrin with a network license."},
  {"releasenetwork",numerrin_releasenetwork,METH_VARARGS,"Release a network license."},
  {"createpool",numerrin_createpool,METH_VARARGS,"Create a new Numerrin variable pool."},
  {"deletepool",numerrin_deletepool,METH_VARARGS,"Delete a Numerrin variable pool."},
  {"clearpool",numerrin_clearpool,METH_VARARGS,"Clear a Numerrin variable pool."},
  {"createcode",numerrin_createcode,METH_VARARGS,"Create a new Numerrin code."},
  {"deletecode",numerrin_deletecode,METH_VARARGS,"Delete a Numerrin code."},
  {"clearcode",numerrin_clearcode,METH_VARARGS,"Clear a Numerrin code."},
  {"parsefile",numerrin_parsefile,METH_VARARGS,"Parse a source code in a file."},
  {"parsestring",numerrin_parsestring,METH_VARARGS,"Parse a source code in a string."},
  {"execute",numerrin_execute,METH_VARARGS,"Execute a parsed code."},
  {"clearvariable",numerrin_clearvariable,METH_VARARGS,"Deletes the contents of a variable."},
  {"gettype",numerrin_gettype,METH_VARARGS,"Get variable type."},
  {"getrank",numerrin_getrank,METH_VARARGS,"Get variable rank."},
  {"getsize",numerrin_getsize,METH_VARARGS,"Get variable sizes."},
  {"getvariable",numerrin_getvariable,METH_VARARGS,"Get variable data."},
  {"putvariable",numerrin_putvariable,METH_VARARGS,"Put a new variable."},
  {"modifyvariable",numerrin_modifyvariable,METH_VARARGS,"Modify variable data."},
  {"getrealfunction",numerrin_getrealfunction,METH_VARARGS,"Get real function data."},
  {"initmesh",numerrin_initmesh,METH_VARARGS,"Initialize a new mesh."},
  {"setnode",numerrin_setnode,METH_VARARGS,"Set coordinates for a mesh node."},
  {"setelementtype",numerrin_setelementtype,METH_VARARGS,"Set type for a mesh element."},
  {"setelement",numerrin_setelement,METH_VARARGS,"Set references for a mesh element."},
  {"meshsize",numerrin_meshsize,METH_VARARGS,"Returns the number of nodes/elements of a mesh."},
  {"getnode",numerrin_getnode,METH_VARARGS,"Returns the coordinates of a mesh node."},
  {"getelement",numerrin_getelement,METH_VARARGS,"Returns the references of a mesh element."},
  {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC initnumerrin(void) {
  Py_InitModule("numerrin",NumerrinMethods);
}

}
