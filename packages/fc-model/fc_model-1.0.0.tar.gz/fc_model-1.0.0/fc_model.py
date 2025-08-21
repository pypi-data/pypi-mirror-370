import json
import os
from typing import Any, TypedDict, List, Dict, Union
from numpy.typing import NDArray

from numpy import dtype, int32, int64, float64

from fc_dict import FCSrcRequiredId
from fc_mesh import FCMesh
from fc_materials import FCMaterial
from fc_conditions import FCLoad, FCInitialSet, FCRestraint
from fc_value import FCValue, decode, encode


class FCHeader(TypedDict):
    binary: bool
    description: str
    version: int
    types: Dict[str, int]


# class FCBlockMaterialSteps(TypedDict):
#     ids: NDArray[int32]
#     steps: NDArray[int32]


class FCSrcBlock(TypedDict):
    id: int
    cs_id: int
    material_id: int
    property_id: int
    # steps: NotRequired[NDArray[int32]]
    # material: NotRequired[FCBlockMaterialSteps]


class FCBlock(FCSrcRequiredId[FCSrcBlock]):
    """
    Определяет 'блок' элементов.
    Блок - это группа элементов, которая ссылается на один и тот же материал
    и имеет общие свойства.
    """
    id: int
    cs_id: int
    material_id: int
    property_id: int

    def __init__(self, src_data: FCSrcBlock):
        self.id = src_data['id']
        self.cs_id = src_data['cs_id']
        self.material_id = src_data['material_id']
        self.property_id = src_data['property_id']

    def dump(self) -> FCSrcBlock:

        return {
            "id": self.id,
            "material_id": self.material_id,
            "property_id": self.property_id,
            "cs_id": self.cs_id,
        }


class FCSrcCoordinateSystem(TypedDict):
    id: int
    type: str
    name: str
    origin: str
    dir1: str
    dir2: str


class FCCoordinateSystem(FCSrcRequiredId[FCSrcCoordinateSystem]):
    id: int
    type: str
    name: str
    origin: NDArray[float64]
    dir1: NDArray[float64]
    dir2: NDArray[float64]


    def __init__(
        self,
        src_data: FCSrcCoordinateSystem
    ):
        self.id = src_data['id']
        self.type = src_data['type']
        self.name = src_data['name']
        self.origin = decode(src_data['origin'], dtype(float64))
        self.dir1 = decode(src_data['dir1'], dtype(float64))
        self.dir2 = decode(src_data['dir2'], dtype(float64))


    def dump(self) -> FCSrcCoordinateSystem:
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "origin": encode(self.origin),
            "dir1": encode(self.dir1),
            "dir2": encode(self.dir2)
        }



class FCSrcConstraint(TypedDict):
    id: int
    name: str
    type: Union[int, str]
    master: str
    master_size: int
    slave: str
    slave_size: int


class FCConstraint(FCSrcRequiredId[FCSrcConstraint]):
    id: int
    name: str
    type: Union[int, str]
    master: FCValue
    slave: FCValue
    properties: Dict[str, Any]

    def __init__(
        self,
        src_data: FCSrcConstraint
    ):
        self.id = src_data['id']
        self.name = src_data['name']
        self.type = src_data['type']
        
        self.master = FCValue(src_data['master'], dtype(int32))
        self.master.resize(src_data['master_size'])
        self.slave = FCValue(src_data['slave'], dtype(int32))
        self.slave.resize(src_data['slave_size'])
        
        self.properties = {
                    key: src_data[key] for key in src_data #type:ignore
                    if key not in FCSrcConstraint.__annotations__.keys()}
        

    def dump(self) -> FCSrcConstraint:

        src_constraint: FCSrcConstraint = {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "master": self.master.dump(),
            "slave": self.slave.dump(),
            "master_size": len(self.master),
            "slave_size": len(self.slave),
        }

        for key in self.properties:
            src_constraint[key] = self.properties[key] #type:ignore

        return src_constraint


class FCSrcSet(TypedDict):
    id: int
    name: str
    apply_to: str
    apply_to_size: int


class FCSet(FCSrcRequiredId[FCSrcSet]):
    id: int
    apply: FCValue
    name: str

    def __init__(self, src_data: FCSrcSet):
        self.apply = FCValue(src_data['apply_to'], dtype(int32))
        self.apply.resize(src_data['apply_to_size'])
        self.id = src_data['id']
        self.name = src_data['name']

    def dump(self) -> FCSrcSet:
        return {
            "apply_to": self.apply.dump(),
            "apply_to_size": len(self.apply),
            "id": self.id,
            "name": self.name
        }


class FCSrcReceiver(TypedDict):
    id: int
    name: str
    apply_to: str
    apply_to_size: int
    dofs: List[int]
    type: int


class FCReceiver(FCSrcRequiredId[FCSrcReceiver]):
    id: int
    apply: FCValue
    dofs: List[int]
    name: str
    type: int

    def __init__(self, src_data: FCSrcReceiver):
        self.apply = FCValue(src_data['apply_to'], dtype(int32))
        self.id = src_data['id']
        self.name = src_data['name']
        self.dofs = src_data['dofs']
        self.type = src_data['type']

    def dump(self) -> FCSrcReceiver:
        return {
            "apply_to": self.apply.dump(),
            "apply_to_size": len(self.apply),
            "id": self.id,
            "name": self.name,
            "dofs": self.dofs,
            "type": self.type
        }


class FCSrcPropertyTable(TypedDict):
    id: int
    type: int
    properties: Dict[str, Any]
    additional_properties: Dict[str, Any]


class FCPropertyTable(FCSrcRequiredId[FCSrcPropertyTable]):
    id: int
    type: int
    properties: Dict[str, Any]
    additional_properties: Dict[str, Any]

    def __init__(self, src_data: FCSrcPropertyTable):
        self.id = src_data['id']
        self.type = src_data.get('type', 0)  # тип может отсутствовать
        self.properties = src_data.get('properties', {})
        self.additional_properties = src_data.get('additional_properties', {})

    def dump(self) -> FCSrcPropertyTable:
        return {
            "id": self.id,
            "type": self.type,
            "properties": self.properties,
            "additional_properties": self.additional_properties
        }



class FCModel:
    """
    Основной класс для представления, загрузки и сохранения модели в формате Fidesys Case (.fc).

    Представляет собой контейнер для всех сущностей модели: узлов, элементов,
    материалов, нагрузок, закреплений и т.д.

    Атрибуты:
        header (FCHeader): Заголовок файла.
        coordinate_systems (Dict[int, FCCoordinateSystem]): Коллекция систем координат.
        elems (FCMesh): Контейнер сетки и элементов.
        blocks (Dict[int, FCBlock]): Коллекция блоков, связывающих элементы с материалами.
        materials (Dict[int, FCMaterial]): Коллекция материалов и их физических свойств.
        loads (List[FCLoad]): Список нагрузок, приложенных к модели.
        restraints (List[FCRestraint]): Список закреплений (ограничений).
        ... и другие коллекции сущностей.

    Пример использования:
    
    # Создание или загрузка модели
    model = FCModel() # Создать пустую модель
    # model = FCModel(filepath="path/to/model.fc") # Загрузить из файла

    # ... (добавление узлов, элементов, материалов)

    # Сохранение модели
    model.save("new_model.fc")
    """

    header: FCHeader = {
        "binary": True,
        "description": "Fidesys Case Format",
        "types": {"char": 1, "short_int": 2, "int": 4, "double": 8, },
        "version": 3
    }

    coordinate_systems: Dict[int, FCCoordinateSystem]

    mesh: FCMesh

    blocks: Dict[int, FCBlock]
    property_tables: Dict[int, FCPropertyTable]
    materials: Dict[int, FCMaterial]

    loads: List[FCLoad]
    restraints: List[FCRestraint]
    initial_sets: List[FCInitialSet]

    contact_constraints: List[FCConstraint]
    coupling_constraints: List[FCConstraint]
    periodic_constraints: List[FCConstraint]

    receivers: List[FCReceiver]

    nodesets: Dict[int, FCSet]
    sidesets: Dict[int, FCSet]

    settings: dict = {}


    def __init__(self, filepath=None):
        """
        Инициализирует объект FCModel.

        Если указан `filepath`, модель будет загружена из этого файла.
        В противном случае будет создана пустая модель с инициализированными коллекциями.

        Args:
            filepath (str, optional): Путь к файлу .fc для загрузки. Defaults to None.
        """
        
        # Инициализация всех коллекций как пустых
        self.coordinate_systems = {}

        self.mesh = FCMesh()

        self.blocks = {}
        self.property_tables = {}
        self.materials = {}
        
        self.loads: List[FCLoad] = []
        self.restraints: List[FCRestraint] = []
        self.initial_sets: List[FCInitialSet] = []

        self.contact_constraints: List[FCConstraint] = []
        self.coupling_constraints: List[FCConstraint] = []
        self.periodic_constraints: List[FCConstraint] = []
        self.receivers: List[FCReceiver] = []

        self.nodesets = {}
        self.sidesets = {}

        if filepath:
            with open(filepath, "r") as f:
                src_data = json.load(f)

            self.src_data = src_data
            self._decode_header(src_data)
            self._decode_blocks(src_data)
            self._decode_coordinate_systems(src_data)
            self._decode_contact_constraints(src_data)
            self._decode_coupling_constraints(src_data)
            self._decode_periodic_constraints(src_data)
            self._decode_mesh(src_data)
            self._decode_settings(src_data)
            self._decode_materials(src_data)
            self._decode_restraints(src_data)
            self._decode_initial_sets(src_data)
            self._decode_loads(src_data)
            self._decode_receivers(src_data)
            self._decode_property_tables(src_data)
            self._decode_sets(src_data)


    def save(self, filepath):
        with open(filepath, "w") as f:
            json.dump(self.dump(), f, indent=4)


    def dump(self):
        """
        Сохраняет текущее состояние модели в файл формата .fc.

        Собирает данные из всех коллекций (узлы, элементы, материалы и т.д.),
        кодирует их в нужный формат (JSON с base64 для бинарных данных)
        и записывает в указанный файл.

        Args:
            filepath (str): Путь к файлу, в который будет сохранена модель.
        """

        output_data: Dict = {}

        self._encode_blocks(output_data)
        self._encode_contact_constraints(output_data)
        self._encode_coordinate_systems(output_data)
        self._encode_coupling_constraints(output_data)
        self._encode_periodic_constraints(output_data)
        self._encode_header(output_data)
        self._encode_loads(output_data)
        self._encode_materials(output_data)
        self._encode_mesh(output_data)
        self._encode_receivers(output_data)
        self._encode_restraints(output_data)
        self._encode_initial_sets(output_data)
        self._encode_settings(output_data)
        self._encode_property_tables(output_data)
        self._encode_sets(output_data)

        return output_data

    def _decode_header(self, input_data):
        self.header = input_data.get('header')

    def _encode_header(self, output_data):
        output_data['header'] = self.header

    def _decode_blocks(self, input_data):
        self.blocks = {}
        for src in input_data.get('blocks', []):
            blk = FCBlock(src)
            self.blocks[blk.id] = blk

    def _encode_blocks(self, output_data):
        if self.blocks:
            output_data['blocks'] = [blk.dump() for blk in self.blocks.values()]

    def _decode_coordinate_systems(self, input_data):
        self.coordinate_systems = {}
        for src in input_data.get('coordinate_systems', []):
            cs = FCCoordinateSystem(src)
            self.coordinate_systems[cs.id] = cs

    def _encode_coordinate_systems(self, output_data):
        if self.coordinate_systems:
            output_data['coordinate_systems'] = [cs.dump() for cs in self.coordinate_systems.values()]


    def _decode_contact_constraints(self, input_data):
        for cc_src in input_data.get('contact_constraints', []):
            self.contact_constraints.append(FCConstraint(cc_src))


    def _encode_contact_constraints(self, output_data):
        if self.contact_constraints:
            output_data['contact_constraints'] = []
            for cc in self.contact_constraints:
                output_data['contact_constraints'].append(cc.dump())

    def _decode_coupling_constraints(self, input_data):
        for cc_src in input_data.get('coupling_constraints', []):
            self.coupling_constraints.append(FCConstraint(cc_src))


    def _encode_coupling_constraints(self, output_data):
        if self.coupling_constraints:
            output_data['coupling_constraints'] = []
            for cc in self.coupling_constraints:
                output_data['coupling_constraints'].append(cc.dump())


    def _decode_periodic_constraints(self, input_data):

        for cc_src in input_data.get('periodic_constraints', []):
            self.periodic_constraints.append(FCConstraint(cc_src))


    def _encode_periodic_constraints(self, output_data):
        if self.periodic_constraints:
            output_data['periodic_constraints'] = []

            for cc in self.periodic_constraints:
                output_data['periodic_constraints'].append(cc.dump())


    def _decode_sets(self, src_data):
        if 'sets' in src_data:
            self.nodesets = {}
            for ns_src in src_data['sets'].get('nodesets', []):
                ns = FCSet(ns_src)
                self.nodesets[ns.id] = ns
            self.sidesets = {}
            for ss_src in src_data['sets'].get('sidesets', []):
                ss = FCSet(ss_src)
                self.sidesets[ss.id] = ss


    def _encode_sets(self,  src_data):
        if not (self.nodesets or self.sidesets):
            return
        src_data['sets'] = {}
        if self.nodesets:
            src_data['sets']['nodesets'] = [ns.dump() for ns in self.nodesets.values()]
        if self.sidesets:
            src_data['sets']['sidesets'] = [ss.dump() for ss in self.sidesets.values()]


    def _decode_mesh(self, src_data):
        self.mesh.decode(src_data['mesh'])

    def _encode_mesh(self, src_data):
        src_data['mesh'] = self.mesh.encode()


    def _decode_settings(self, src_data):
        self.settings = src_data.get('settings')

    def _encode_settings(self, src_data):
        src_data['settings'] = self.settings

    def _decode_property_tables(self, src_data):
        self.property_tables = {}
        for pt_src in src_data.get('property_tables', []):
            pt = FCPropertyTable(pt_src)
            self.property_tables[pt.id] = pt

    def _encode_property_tables(self, src_data):
        if self.property_tables:
            src_data['property_tables'] = [pt.dump() for pt in self.property_tables.values()]


    def _decode_materials(self, src_data):
        self.materials = {}
        for src_material in src_data.get('materials', []):
            material = FCMaterial(src_material)
            self.materials[material.id] = material


    def _encode_materials(self, src_data):
        if self.materials:
            src_data['materials'] = [mat.dump() for mat in self.materials.values()]


    def _decode_loads(self, input_data):
        for src_load in input_data.get('loads', []):
            self.loads.append(FCLoad(src_load))


    def _encode_loads(self, output_data):
        if self.loads:
            output_data['loads'] = []
            for load in self.loads:
                output_data['loads'].append(load.dump())

    def _decode_restraints(self, input_data):
        for src_restraint in input_data.get('restraints', []):
            self.restraints.append(FCRestraint(src_restraint))

    def _encode_restraints(self, output_data):
        if self.restraints:
            output_data['restraints'] = []
            for restraint in self.restraints:
                output_data['restraints'].append(restraint.dump())

    def _decode_initial_sets(self, input_data):
        for src_initial_set in input_data.get('initial_sets', []):
            self.initial_sets.append(FCInitialSet(src_initial_set))

    def _encode_initial_sets(self, output_data):
        if self.initial_sets:
            output_data['initial_sets'] = []
            for initial_set in self.initial_sets:
                output_data['initial_sets'].append(initial_set.dump())

    def _decode_receivers(self, input_data):
        for src_receiver in input_data.get('receivers', []):
            self.receivers.append(FCReceiver(src_receiver))

    def _encode_receivers(self, output_data):
        if self.receivers:
            output_data['receivers'] = []
            for receiver in self.receivers:
                output_data['receivers'].append(receiver.dump())



if __name__ == '__main__':
    name = "ultacube"
    datapath = "/home/antonov/Base/Libs/FCModel/data/"

    inputpath = os.path.join(datapath, f"{name}.fc")
    outputpath = os.path.join(datapath, f"{name}_roundtrip.fc")

    fc_model = FCModel(inputpath)

    fc_model.save(outputpath)  # ОШИБКА: Метод dump() не принимает аргументы
