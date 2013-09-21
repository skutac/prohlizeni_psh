function Tagcloud(element_id, user_settings){
    var element_width = $("#" + element_id).width();
    this.settings = {
        "element_id" : element_id,
        "min_font_size": 22,
        "max_font_size": 62,
        "width": element_width,
        "color_scale": "Blues",
        "class_count": 10,
        "font": "Trebuchet MS",
        "colors" :{
            "YlGn": {"start": {"r":255, "g": 255, "b": 204}, "end": {"r": 35, "g": 132, "b": 67}},
            "YlGnBu": {"start": {"r":255, "g": 255, "b": 204}, "end": {"r": 34, "g": 94, "b": 168}},
            "GnBu": {"start": {"r":240, "g": 249, "b": 232}, "end": {"r": 43, "g": 140, "b": 190}},
            "BuGn": {"start": {"r":237, "g": 248, "b": 251}, "end": {"r": 35, "g": 139, "b": 69}},
            "PuBuGn": {"start": {"r":246, "g": 239, "b": 247}, "end": {"r": 2, "g": 129, "b": 138}},
            "PuBu": {"start": {"r":241, "g": 238, "b": 246}, "end": {"r": 5, "g": 112, "b": 176}},
            "BuPu": {"start": {"r":237, "g": 248, "b": 251}, "end": {"r": 136, "g": 65, "b": 157}},
            "RdPu": {"start": {"r":254, "g": 235, "b": 226}, "end": {"r": 174, "g": 1, "b": 126}},
            "PuRd": {"start": {"r":241, "g": 238, "b": 246}, "end": {"r": 206, "g": 18, "b": 86}},
            "OrRd:": {"start": {"r":254, "g": 240, "b": 217}, "end": {"r": 215, "g": 48, "b": 31}},
            "YlOrR": {"start": {"r":255, "g": 255, "b": 178}, "end": {"r": 227, "g": 26, "b": 28}},
            "YlOrB": {"start": {"r":255, "g": 255, "b": 212}, "end": {"r": 204, "g": 76, "b": 2}},
            "Purples2": {"start": {"r":242, "g": 240, "b": 247}, "end": {"r": 106, "g": 81, "b": 163}},
            "Blues": {"start": {"r":239, "g": 243, "b": 255}, "end": {"r": 33, "g": 113, "b": 181}},
            "Greens": {"start": {"r":237, "g": 248, "b": 233}, "end": {"r": 35, "g": 139, "b": 69}},
            "Oranges": {"start": {"r":254, "g": 237, "b": 222}, "end": {"r": 217, "g": 71, "b": 1}},
            "Reds": {"start": {"r":254, "g": 229, "b": 217}, "end": {"r": 203, "g": 24, "b": 29}},
            "Greys": {"start": {"r":247, "g": 247, "b": 247}, "end": {"r": 82, "g": 82, "b": 82}},
            "PuOr": {"start": {"r":230, "g": 97, "b": 1}, "end": {"r": 94, "g": 60, "b": 153}},
            "BrBG": {"start": {"r":166, "g": 97, "b": 26}, "end": {"r": 1, "g": 133, "b": 113}},
            "PRGn2": {"start": {"r":123, "g": 50, "b": 148}, "end": {"r": 0, "g": 136, "b": 55}},
            "PiYG2": {"start": {"r":208, "g": 28, "b": 139}, "end": {"r": 77, "g": 172, "b": 38}},
            "RdBu": {"start": {"r":202, "g": 0, "b": 32}, "end": {"r": 5, "g": 113, "b": 176}},
            "RdGy": {"start": {"r":202, "g": 0, "b": 32}, "end": {"r": 64, "g": 64, "b": 64}},
            "RdYlBu": {"start": {"r":215, "g": 25, "b": 28}, "end": {"r": 44, "g": 123, "b": 182}},
            "Spectral": {"start": {"r":215, "g": 25, "b": 28}, "end": {"r": 43, "g": 131, "b": 186}},
            "RdYlGn": {"start": {"r":215, "g": 25, "b": 28}, "end": {"r": 26, "g": 150, "b": 65}},
        },
    };

    $.extend(this.settings, user_settings);

    this.text_ref = new Kinetic.Text({
    	fontFamily: this.settings.font,
    });
}

Tagcloud.prototype.read_data = function(data){
	this.data = data;
	this.tag2font_size = this.calculate_font_size(data);
}

Tagcloud.prototype.calculate_font_size = function(data){
	var values = [], i, tag2font_size = {};

	for(i in data){
		values.push(data[i]);
	};

	this.min_value = Math.min.apply(null, values);
	this.max_value = Math.max.apply(null, values);
	var numbers_extent = this.max_value - this.min_value;
	var class_font_size = (this.settings.max_font_size - this.settings.min_font_size)/this.settings.class_count;
	var class_size = numbers_extent/this.settings.class_count;

	for(i in data){
		tag2font_size[i] = this.hack_round(this.settings.min_font_size + (data[i] - this.min_value)/class_size*class_font_size);
	};
	return tag2font_size;
}

Tagcloud.prototype.draw = function(){
	var i, j, tag, tags = [];

	this.stage = new Kinetic.Stage({
        container: this.settings.element_id,
        width: this.settings.width,
        height: 1000,
    });

    this.tagcloud_layer = new Kinetic.Layer();
    this.stage.add(this.tagcloud_layer);

    for(i in this.tag2font_size){
    	tag = this.draw_tag(i, this.tag2font_size[i]);
    	tags.push(tag);
    }

    var row = [];
    var row_length = 0;
    var tag_width;

    for(i = 0; i<tags.length; i++){
    	for(j = 0; j<tags[i].children.length; j++){
    		row_length = row_length + tags[i].children[j].getWidth();
    		console.log(tags[i].children[j].getWidth())
    		row.push(tags[i].children[j]);
    	}
    	if(row_length > this.settings.width){
    		console.log(row_length);
    		row = [tags[i].children[j]];
    		row_length = tags[i].children[j].getWidth();
    	}
    }

    // this.tagcloud_layer.draw();
}

Tagcloud.prototype.draw_tag = function(tag, font_size){
	var color = this.get_color_for_value(font_size, this.settings.min_font_size, this.settings.max_font_size, this.settings.color_scale);
	var split = tag.split(" ");
	var group = new Kinetic.Group();
	var i = 0, tag;

	for(i; i<split.length; i++){
		tag = this.text_ref.clone({
			text: split[i],
			fontSize: font_size,
			x: 0,
			y: 100,
			fill: color,
		});
		group.add(tag);
	}
	return group;
}

Tagcloud.prototype.hack_round = function(value){
    return (0.5 + value) >> 0;
}

Tagcloud.prototype.get_color_for_value = function(value, min, max, color_scale){
    var color = this.settings.colors[color_scale];

    var r1 = color["end"]["r"];
    var g1 = color["end"]["g"];
    var b1 = color["end"]["b"];
    
    var r2 = color["start"]["r"];
    var g2 = color["start"]["g"];
    var b2 = color["start"]["b"];

    if(min == max){
        return 'rgb('+r2+','+g2+','+b2+')';
    }

    var position = (value-min)/(max-min);
    
    var r = this.hack_round(r2+(position*(r1-r2)));
    var g = this.hack_round(g2+(position*(g1-g2)));
    var b = this.hack_round(b2+(position*(b1-b2)));
    
    color = 'rgb('+r+','+g+','+b+')';
    return color;
}